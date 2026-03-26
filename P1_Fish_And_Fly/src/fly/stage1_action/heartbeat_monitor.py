import time

from src.common.logging import logger
from src.common.logging.entity import CoverageArea
from src.common.entity.heartbeat import SystemHeartbeat

from src.fly.stage1_action.entity import MonitorConfig, StateDeltas, FishStatus



class HeartbeatMonitor:
    def __init__(self, monitor_config: MonitorConfig):
        self.timeout = monitor_config.timeout_sec                                                           # hard death 
        self.freeze = monitor_config.freeze_sec                                                             # soft freeze

        self.last_received_ts = None                                                                        # last time, heartbeat recieved by Fly (ts = timestamp)
        self.last_fish_ts = None                                                                            # last time, heartbeat sent from Fish



    # Implemented Cross-system reconciliation logic
    def calculate_fish_state_deltas(self, heartbeat: SystemHeartbeat, coverage_area_pcts: CoverageArea) -> StateDeltas:
        try:
            logger.info(f"HeartbeatMonitor -> calculate_fish_state_deltas(): STARTS, heartbeat: {heartbeat}")

            curr_time = time.time()                                                                         # Fly's clock
            curr_emitted_fish_ts = heartbeat.timestamp                                                      # Fish's clock

            # 1. In case of First heartbeat, intitializes 
            if (self.last_received_ts is None) or (self.last_fish_ts is None):
                self.last_received_ts = curr_time
                self.last_fish_ts = curr_emitted_fish_ts

                state_deltas = StateDeltas(
                    mission_phase= heartbeat.mission_phase.name,
                    fish_state= FishStatus.INIT.name,
                    fish_x= heartbeat.position.x,
                    fish_y= heartbeat.position.y,
                    fish_z= heartbeat.position.z,
                    surface_coverage_pct= coverage_area_pcts.surface_percentage,
                    underwater_coverage_pct= coverage_area_pcts.underwater_percentage,
                    communication_delta= 0.0,
                    fish_progress_delta= 0.0,
                    silence_delta= 0.0
                )

                logger.info(f"HeartbeatMonitor -> calculate_fish_state_deltas(), state_delats: {state_deltas}")
                return state_deltas


            # 2. Calculating the 3 delta values

            # Delta1: Silence (True death detection)
            silence_delta = curr_time - self.last_received_ts

            # Delta2: Communication / Scheduling lag
            communication_delta = curr_time - curr_emitted_fish_ts

            # Delat3: Fish Execution freeze (Fish clock not progressing)
            fish_progress_delta = curr_emitted_fish_ts - self.last_fish_ts


            # 3. Deciding the status of Fish
            if silence_delta > self.timeout:
                state_deltas = StateDeltas(
                    mission_phase= heartbeat.mission_phase.name,
                    fish_state= FishStatus.DEAD.name,
                    fish_x= heartbeat.position.x,
                    fish_y= heartbeat.position.y,
                    fish_z= heartbeat.position.z,
                    surface_coverage_pct= coverage_area_pcts.surface_percentage,
                    underwater_coverage_pct= coverage_area_pcts.underwater_percentage,
                    communication_delta= communication_delta,
                    fish_progress_delta= fish_progress_delta,
                    silence_delta= silence_delta
                )

                logger.info(f"HeartbeatMonitor -> calculate_fish_state_deltas(), state_delats: {state_deltas}")
                return state_deltas
            

            # In case when Fish is not DEAD
            curr_status= FishStatus.ALIVE

            if communication_delta > self.freeze:
                curr_status = FishStatus.LAGGING
            
            if fish_progress_delta <= 1e-3:
                curr_status = FishStatus.FROZEN


            state_deltas = StateDeltas(
                mission_phase= heartbeat.mission_phase.name,
                fish_state= curr_status.name,
                fish_x= heartbeat.position.x,
                fish_y= heartbeat.position.y,
                fish_z= heartbeat.position.z,
                surface_coverage_pct= coverage_area_pcts.surface_percentage,
                underwater_coverage_pct= coverage_area_pcts.underwater_percentage,
                communication_delta= communication_delta,
                fish_progress_delta= fish_progress_delta,
                silence_delta= silence_delta
            )

            # Update timestamps
            self.last_received_ts = curr_time
            self.last_fish_ts = curr_emitted_fish_ts

            logger.info(f"HeartbeatMonitor -> calculate_fish_state_deltas(): ENDS, state_delats: {state_deltas}")
            return state_deltas


        except Exception as e:
            logger.info(f"HeartbeatMonitor -> calculate_fish_state_deltas(), error: {e}")
            raise e