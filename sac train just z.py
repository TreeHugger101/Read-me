import os


import ctypes
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor
from stable_baselines3.common.utils import set_random_seed


# ============================================================
# CONFIG
# ============================================================

DLL_PATH = r"A:\UAV6\Copy_of_s97_offline_4codegen_20251202_win64.dll"
MODEL_PATH = "uav_sac_controller1"

TOTAL_TIMESTEPS = 10_000_000
N_ENVS = 20
MAX_EP_STEPS = 15000
INNIT_Z=-5200
# Targets
U_TARGET = 70.0
Z_TARGET = -5500.0

# Action scaling
THR_MIN = 50.0
THR_MAX = 100.0
ROLL_MAX = 45.0
PITCH_MAX = 10.0

# Normalization
U_MAX = 120.0
W_MAX = 20.0
PQR_MAX = 2.0
ALT_ERR_MAX = 100.0


# ============================================================
# ENVIRONMENT
# ============================================================

class UAVEnv(gym.Env):

    def __init__(self):
        super().__init__()

        self.lib = ctypes.CDLL(DLL_PATH)

        class ExtU(ctypes.Structure):
            _fields_ = [
                ("RollCmd", ctypes.c_double),
                ("PitchCmd", ctypes.c_double),
                ("ThrCmd", ctypes.c_double),
            ]

        class ExtY(ctypes.Structure):
            _fields_ = [
                ("State", ctypes.c_double * 15),
                ("crash", ctypes.c_bool),
            ]

        self.U = ExtU.in_dll(self.lib, "Copy_of_s97_offline_4codegen_20251202_U")
        self.Y = ExtY.in_dll(self.lib, "Copy_of_s97_offline_4codegen_20251202_Y")

        self.initialize = self.lib.Copy_of_s97_offline_4codegen_20251202_initialize
        self.output_fn  = self.lib.Copy_of_s97_offline_4codegen_20251202_output
        self.update     = self.lib.Copy_of_s97_offline_4codegen_20251202_update
        self.terminate  = self.lib.Copy_of_s97_offline_4codegen_20251202_terminate

        self.action_space = spaces.Box(
            low=np.array([0.0, -1.0, -1.0], dtype=np.float32),
            high=np.array([1.0,  1.0,  1.0], dtype=np.float32),
        )

        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(26,),
            dtype=np.float32,
        )

        self.step_count = 0
        self.previous_z=INNIT_Z
        self.InGoal=0
        self.previous_altError=0 
        self.reward=0 
        self.episode_id=0      


    # --------------------------------------------------------

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.initialize()
        self.step_count = 0
        self.previous_z=INNIT_Z
        self.InGoal=0
        self.previous_altError=0
        self.reward=0
        self.episode_id+=1
        return self._get_obs(), {}


    # --------------------------------------------------------

    def _get_obs(self):

        s = np.array(self.Y.State, dtype=np.float64)
        s = np.clip(s, -1e5, 1e5)

        roll, pitch, yaw = s[3], s[4], s[5]
        u, v, w = s[6], s[7], s[8]
        p, q, r = s[9], s[10], s[11]
        z = s[2]

        airspeed_error = u - U_TARGET
        altitude_error = z - Z_TARGET

        obs = np.zeros(26, dtype=np.float32)

        # Orientation
        obs[0] = np.sin(roll)
        obs[1] = np.cos(roll)
        obs[2] = np.sin(pitch)
        obs[3] = np.cos(pitch)
        obs[4] = np.sin(yaw)
        obs[5] = np.cos(yaw)

        # Rates
        obs[6] = np.clip(p / PQR_MAX, -1, 1)
        obs[7] = np.clip(q / PQR_MAX, -1, 1)
        obs[8] = np.clip(r / PQR_MAX, -1, 1)

        # Velocities
        obs[9]  = np.clip(u / U_MAX, -1, 1)
        obs[10] = np.clip(v / U_MAX, -1, 1)
        obs[11] = np.clip(w / W_MAX, -1, 1)

        # Errors
        obs[12] = np.clip(airspeed_error / U_MAX, -1, 1)
        obs[13] = np.clip(altitude_error / ALT_ERR_MAX, -1, 1)

        # Bias
        obs[14] = 0.0
        obs[15] = 1.0

        # Unused
        obs[16:25] = 0.0
        obs[25] = 0.0

        return obs


    # --------------------------------------------------------

    def step(self, action):

        thr_cmd   = THR_MIN + (THR_MAX - THR_MIN) * float(action[0])
        roll_cmd  = float(action[1]) * ROLL_MAX
        pitch_cmd = float(action[2]) * PITCH_MAX

        self.U.ThrCmd   = thr_cmd
        self.U.RollCmd  = roll_cmd
        self.U.PitchCmd = pitch_cmd

        self.output_fn()
        self.update()

        s = np.array(self.Y.State, dtype=np.float64)
        
        if not np.all(np.isfinite(s)):
            return self._get_obs(), -500.0, True, False, {}


        z = s[2]
        u = s[6]
        v = s[7]
        w = s[8]
        q = s[10]

        alt_err = z - Z_TARGET
        speed_err = u - U_TARGET

        terminated = False
        truncated = False

        # ========== safety ==========
        if not np.all(np.isfinite(s)) or abs(z) > 1e6:
            return self._get_obs(), -500.0, True, False, {}

        # ========== reward ==========

        reward = 0.0

        if z > Z_TARGET-50:
            reward=z**2/100000000
        else:
            reward=-z**2/100000000

        if abs(z-Z_TARGET)<50:
            self.InGoal+=1
        reward = float(np.clip(reward, -10, 10))

        self.step_count += 1
        self.reward += reward

        if self.Y.crash:
            terminated = True
            reward -= 300

        if self.step_count >= MAX_EP_STEPS:
            truncated = True
            
            print(
                f"[EP {self.episode_id}] "
                f"Final Altitude: {z} m | "
                f"Total Reward: {self.reward} | "
                f"Goal Steps: {self.InGoal}"
    )

        return self._get_obs(), reward, terminated, truncated, {}


    def close(self):
        self.terminate()


# ============================================================
# PARALLEL ENV
# ============================================================

def make_env(rank, seed=0):
    def _init():
        env = UAVEnv()
        env.reset(seed=seed + rank)
        return env
    return _init


# ============================================================
# TRAIN
# ============================================================

if __name__ == "__main__":

    set_random_seed(0)

    env = SubprocVecEnv([make_env(i) for i in range(N_ENVS)])
    env = VecMonitor(env)

    if os.path.exists(MODEL_PATH + ".zip"):
        print("Loading SAC model...")
        model = SAC.load(MODEL_PATH, env=env, device="cpu", verbose=0 )
    
        model.ent_coef = 0.0001

    else:
        print("Creating SAC model...")

        model = SAC(
            "MlpPolicy",
            env,
            learning_rate=3e-4,
            batch_size=256,
            buffer_size=1_000_000,
            gamma=0.995,
            tau=0.005,
            ent_coef="auto",
            train_freq=1,
            gradient_steps=1,
            verbose=0,
            device="cpu"
        )

    model.learn(total_timesteps=TOTAL_TIMESTEPS)
    model.save(MODEL_PATH)

    print("✅ SAC training complete:", MODEL_PATH)
