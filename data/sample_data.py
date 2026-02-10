"""
Sample Data Generator for Delivery Excellence Dashboard

Generates realistic delivery metrics data for demonstration purposes.
This module creates synthetic but realistic data for:
- Sprint velocity and capacity planning
- Defect density and quality metrics
- Resource utilization and team allocation
- Customer satisfaction trends
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_velocity_data(num_sprints: int = 12) -> pd.DataFrame:
    """
    Generate sprint velocity data with realistic variance.

    Args:
        num_sprints: Number of sprints to generate (default: 12 = 3 quarters)

    Returns:
        DataFrame with columns: Sprint, Planned_Points, Completed_Points, Capacity
    """
    np.random.seed(42)

    base_velocity = 45
    sprints = []

    for i in range(num_sprints):
        # Realistic velocity with some variance
        completed = base_velocity + np.random.normal(0, 5)
        planned = base_velocity + np.random.normal(2, 6)
        capacity = base_velocity + 5  # Slight buffer

        sprints.append({
            'Sprint': f'Sprint {i+1}',
            'Sprint_Number': i + 1,
            'Planned_Points': max(30, int(planned)),
            'Completed_Points': max(25, int(completed)),
            'Capacity': max(35, int(capacity)),
            'Planned_Date': (datetime.now() - timedelta(days=14*(num_sprints-i))).strftime('%Y-%m-%d')
        })

    return pd.DataFrame(sprints)


def generate_defect_data(num_sprints: int = 12) -> pd.DataFrame:
    """
    Generate defect density data (bugs per 1000 lines of code).

    Realistic data shows:
    - Generally stable quality (~3-4 bugs/1000 LOC)
    - Occasional spikes when shipping hard features
    - Overall downward trend (improvement)

    Args:
        num_sprints: Number of sprints to generate

    Returns:
        DataFrame with columns: Sprint, Defects, LOC, Defect_Density
    """
    np.random.seed(42)

    sprints = []
    base_density = 4.0

    for i in range(num_sprints):
        # Slightly improving trend with noise
        trend = max(1.5, base_density - (i * 0.15))
        density = trend + np.random.normal(0, 0.8)

        # Generate supporting metrics
        loc = int(np.random.normal(12000, 1500))
        defects = max(0, int(density * loc / 1000))

        sprints.append({
            'Sprint': f'Sprint {i+1}',
            'Sprint_Number': i + 1,
            'Defects': defects,
            'LOC_Added': loc,
            'Defect_Density': round(density, 2),
            'Defect_Status': 'Critical' if density > 6 else ('Warning' if density > 4 else 'Healthy')
        })

    return pd.DataFrame(sprints)


def generate_resource_data() -> pd.DataFrame:
    """
    Generate resource utilization data across teams.

    Returns:
        DataFrame with columns: Team, Allocated_Hours, Available_Hours, Utilization_Percent
    """
    teams = [
        {'Team': 'Backend Engineering', 'Members': 6, 'Allocated': 450, 'Available': 480},
        {'Team': 'Frontend Engineering', 'Members': 5, 'Allocated': 360, 'Available': 400},
        {'Team': 'QA & Testing', 'Members': 4, 'Allocated': 280, 'Available': 320},
        {'Team': 'DevOps & Infrastructure', 'Members': 2, 'Allocated': 150, 'Available': 160},
        {'Team': 'Product Management', 'Members': 2, 'Allocated': 140, 'Available': 160},
    ]

    for team in teams:
        team['Utilization_Percent'] = round((team['Allocated'] / team['Available']) * 100, 1)
        team['Headroom'] = team['Available'] - team['Allocated']

    return pd.DataFrame(teams)


def generate_csat_data(num_sprints: int = 12) -> pd.DataFrame:
    """
    Generate Customer Satisfaction (CSAT) trend data.

    Realistic data shows:
    - Generally high satisfaction (4.0-4.5 out of 5.0)
    - Seasonal variations
    - Slight improvement trend
    - Dips after major releases

    Args:
        num_sprints: Number of sprints to generate

    Returns:
        DataFrame with columns: Sprint, CSAT_Score, Responses, NPS
    """
    np.random.seed(42)

    sprints = []
    base_score = 4.0

    for i in range(num_sprints):
        # Slight improvement trend with realistic variance
        trend = min(4.6, base_score + (i * 0.05))
        score = trend + np.random.normal(0, 0.2)
        score = max(3.0, min(5.0, score))  # Clamp between 3 and 5

        # NPS score (Net Promoter Score) - derived from CSAT
        nps = int((score - 3) * 25)  # Rough correlation

        # Survey response rate
        responses = np.random.randint(40, 80)

        sprints.append({
            'Sprint': f'Sprint {i+1}',
            'Sprint_Number': i + 1,
            'CSAT_Score': round(score, 2),
            'Responses': responses,
            'NPS_Score': nps,
            'Status': 'Excellent' if score >= 4.3 else ('Good' if score >= 3.8 else 'Fair')
        })

    return pd.DataFrame(sprints)


def generate_burndown_data(sprint_number: int = 12) -> pd.DataFrame:
    """
    Generate detailed burndown data for the current sprint.

    Args:
        sprint_number: Which sprint number to generate burndown for

    Returns:
        DataFrame with columns: Day, Ideal_Remaining, Actual_Remaining
    """
    np.random.seed(42 + sprint_number)

    days = 10  # Typical 2-week sprint with 10 working days
    burndown = []

    # Ideal burndown - linear decrease
    total_points = 50

    for day in range(days + 1):
        ideal = max(0, total_points * (1 - day / days))

        # Actual burndown with realistic patterns:
        # - Slow start (days 1-2)
        # - Faster middle (days 3-7)
        # - Slowdown at end (days 8-10)
        if day <= 2:
            variance = np.random.normal(0, 3)
        elif day <= 7:
            variance = np.random.normal(-2, 2)  # Ahead of ideal
        else:
            variance = np.random.normal(2, 3)   # Slipping slightly

        actual = max(0, ideal + variance)

        burndown.append({
            'Day': day,
            'Day_Label': f'Day {day}' if day > 0 else 'Sprint Start',
            'Ideal_Remaining': round(ideal, 1),
            'Actual_Remaining': round(actual, 1)
        })

    return pd.DataFrame(burndown)


def get_all_data() -> dict:
    """
    Generate all sample data sets.

    Returns:
        Dictionary containing all data frames
    """
    return {
        'velocity': generate_velocity_data(),
        'defects': generate_defect_data(),
        'resources': generate_resource_data(),
        'csat': generate_csat_data(),
        'burndown': generate_burndown_data()
    }


if __name__ == '__main__':
    """
    Demo script to show sample data generation.
    """
    print("Generating sample delivery metrics data...\n")

    # Generate all data
    data = get_all_data()

    # Display samples
    print("=" * 60)
    print("VELOCITY DATA (Last 3 Sprints)")
    print("=" * 60)
    print(data['velocity'][['Sprint', 'Planned_Points', 'Completed_Points', 'Capacity']].tail(3))

    print("\n" + "=" * 60)
    print("DEFECT DENSITY (Last 3 Sprints)")
    print("=" * 60)
    print(data['defects'][['Sprint', 'Defects', 'Defect_Density', 'Defect_Status']].tail(3))

    print("\n" + "=" * 60)
    print("RESOURCE UTILIZATION")
    print("=" * 60)
    print(data['resources'][['Team', 'Members', 'Utilization_Percent', 'Headroom']])

    print("\n" + "=" * 60)
    print("CUSTOMER SATISFACTION (Last 3 Sprints)")
    print("=" * 60)
    print(data['csat'][['Sprint', 'CSAT_Score', 'NPS_Score', 'Status']].tail(3))

    print("\n" + "=" * 60)
    print("CURRENT SPRINT BURNDOWN")
    print("=" * 60)
    print(data['burndown'][['Day_Label', 'Ideal_Remaining', 'Actual_Remaining']])

    print("\n✓ Sample data generation complete!")
