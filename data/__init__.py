"""
Data module for Delivery Excellence Dashboard

Provides sample data generation for metrics visualization.
"""

from .sample_data import (
    generate_velocity_data,
    generate_defect_data,
    generate_resource_data,
    generate_csat_data,
    generate_burndown_data,
    get_all_data
)

__all__ = [
    'generate_velocity_data',
    'generate_defect_data',
    'generate_resource_data',
    'generate_csat_data',
    'generate_burndown_data',
    'get_all_data'
]
