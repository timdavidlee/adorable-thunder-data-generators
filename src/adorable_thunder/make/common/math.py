import numpy as np
from enum import Enum


def round_weights_and_rebalance(weights: np.ndarray, precision: int = 4) -> np.ndarray:
    """
    Rounds the weights to the specified precision and rebalances them to ensure they sum to 1.
    Args:
        weights: The array of weights to round and rebalance. Must sum to 1.
        precision: The number of decimal places to round the weights to. Higher values will result in more precise weights, but may also result in weights that do not sum to 1 due to rounding errors.
    """
    rounded_weights = np.round(weights, decimals=precision)
    diff = 1 - rounded_weights.sum()
    rounded_weights[0] += diff
    return rounded_weights


def get_weights(
    num_items: int, power_scale: float = 2.0, precision: int = 4
) -> np.ndarray:
    """
    Args:
        num_items: The number of items to generate weights for
        power_scale: The power to which the rank of the item is raised. Higher values will result in a more skewed distribution.
        precision: The number of decimal places to round the weights to. Higher values will result in more precise weights, but may also result in weights that do not sum to 1 due to rounding errors.
    """
    weights = 1 / (np.arange(1, num_items + 1) ** power_scale)
    weights = weights / weights.sum()
    rounded_weights = round_weights_and_rebalance(weights, precision=precision)
    return rounded_weights


def generate_weighted_random_choice(
    items: list[str], n_samples: int, weights: np.ndarray
) -> np.ndarray:
    """
    Args:
        items: The list of items to choose from
        n_samples: The number of samples to generate
        weights: The weights corresponding to each item. Must sum to 1.
    """
    return np.random.choice(items, p=weights, size=n_samples)


def generate_weighted_enum_choices(
    enum_cls: type[Enum], num_samples: int, power_scale: float = 1.5, precision: int = 4
) -> np.ndarray:
    """
    Args:
        enum_cls: The enum class to generate choices from
        num_samples: The number of samples to generate
        power_scale: The power to which the rank of the item is raised. Higher values will result in a more skewed distribution.
        precision: The number of decimal places to round the weights to. Higher values will result in more precise weights, but may also result in weights that do not sum to 1 due to rounding errors.
    """
    items = [item.value for item in list(enum_cls)]
    weights = get_weights(
        num_items=len(items), power_scale=power_scale, precision=precision
    )
    return generate_weighted_random_choice(
        items, n_samples=num_samples, weights=weights
    )
