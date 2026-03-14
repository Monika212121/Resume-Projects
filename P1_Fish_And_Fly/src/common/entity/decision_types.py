from enum import Enum



class DecisionStatus(Enum):
   TARGET_SELECTED = "high priority, safe object"                                            # current selected object
   TARGET_IGNORED = "low priority, safe object"                                              # these objects will be selected later
   TARGET_AVOIDED = "near hazard, unsafe object"                                             # these objects will never be selected
   ENVIRONMENT_OBJECT_IGNORED = "harmless aquatic beings"                                    # these objects will never be selected
   HAZARD_OBJECT_AVOIDED = "harmful animal or large rock"                                    # these objects will never be selected
