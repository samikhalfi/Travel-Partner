import pandas as pd
import plotly.express as px
import streamlit as st

def estimate_trip_budget(destination, duration=7):

    try:
        # Simulated budget estimation (would use more sophisticated API in production)
        base_costs = {
            'accommodation': 100 * duration,
            'food': 50 * duration,
            'local_transport': 20 * duration,
            'attractions': 30 * duration,
            'miscellaneous': 50
        }
        total_estimated_budget = sum(base_costs.values())
        
        return {
            'total_estimated_budget': total_estimated_budget,
            'cost_breakdown': base_costs
        }
    except Exception as e:
        st.error(f"Budget estimation error: {e}")
        return None

def generate_budget_visualization(budget_info):
    """
    Create a budget breakdown visualization
    
    Args:
        budget_info (dict): Budget information dictionary
    
    Returns:
        plotly figure: Budget breakdown pie chart
    """
    if not budget_info:
        return None
    
    df = pd.DataFrame.from_dict(budget_info['cost_breakdown'], orient='index', columns=['Cost'])
    df.index.name = 'Category'
    df = df.reset_index()
    
    fig = px.pie(df, values='Cost', names='Category', 
                 title='Travel Budget Breakdown',
                 color_discrete_sequence=px.colors.sequential.Plasma_r)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig