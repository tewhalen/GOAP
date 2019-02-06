from enum import auto, Enum
from typing import NamedTuple, Dict, Any


class EvaluationState(Enum):
    failure = auto()
    success = auto()
    running = auto()


class EffectReference(NamedTuple):
    """Container class to allow a service-API for plugins"""

    forwarded_effect_name: str


def reference(name: str) -> EffectReference:
    """Convenience function to return Forwarder object"""
    return EffectReference(name)


# WARNING: Deprecated
expose = reference


class ActionValidator(type):
    def __new__(metacls, cls_name, bases, attrs):
        if bases:
            # Validate precondition plugins
            preconditions = attrs.get("preconditions", {})
            # Overwrite effect plugins to ellipsis
            all_effects = attrs.get("effects", {})
            metacls._validate_preconditions(all_effects, preconditions)

        return super().__new__(metacls, cls_name, bases, attrs)

    @staticmethod
    def _validate_preconditions(all_effects, preconditions):
        for name, value in preconditions.items():
            if value is Ellipsis:
                raise ValueError("Invalid value for precondition '{}'".format(name))

            elif hasattr(value, "forwarded_effect_name") and value.forwarded_effect_name not in all_effects:
                raise ValueError("Invalid plugin name for precondition '{}': {!r}".format(name, value.name))


class Action(metaclass=ActionValidator):
    cost: int = 1
    precedence: int = 0

    effects: Dict[str, Any] = {}
    preconditions: Dict[str, Any] = {}

    apply_effects_on_exit: bool = True

    def __repr__(self) -> str:
        return "<Action {!r}>".format(self.__class__.__name__)

    def apply_effects(self, world_state: Dict[str, Any], goal_state: Dict[str, Any]):
        """Apply action effects to state, resolving any variables from goal state

        :param world_state: state to modify
        :param goal_state: source for variables
        """
        for key, value in self.effects.items():
            if value is Ellipsis:
                value = goal_state[key]

            world_state[key] = value

    def check_procedural_precondition(
        self, world_state: Dict[str, Any], goal_state: Dict[str, Any], is_planning: bool = True
    ) -> bool:
        return True

    def get_status(self, world_state: Dict[str, Any], goal_state: Dict[str, Any]) -> EvaluationState:
        return EvaluationState.success

    def get_cost(self, world_state: Dict[str, Any], goal_state: Dict[str, Any]) -> int:
        return self.cost

    def on_enter(self, world_state: Dict[str, Any], goal_state: Dict[str, Any]):
        pass

    def on_exit(self, world_state: Dict[str, Any], goal_state: Dict[str, Any]):
        pass
