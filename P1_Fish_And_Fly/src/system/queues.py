import asyncio


fish_control_signal_queue = asyncio.Queue(maxsize = 20)
fish_heartbeat_queue = asyncio.Queue(maxsize = 20)
dispatch_order_queue = asyncio.Queue(maxsize= 20)
dispatch_outcome_queue = asyncio.Queue(maxsize= 20)