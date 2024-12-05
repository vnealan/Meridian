import json
from datetime import datetime
from typing import List, Dict, Tuple

def calculate_workload_capacity(current_score: float) -> Dict:
    """
    Calculate recommended workload adjustment based on wellbeing score.
    
    Args:
        current_score: Wellbeing score between 0 and 1
    
    Returns:
        Dictionary containing workload adjustment recommendations
    """
    # Base calculation: Linear interpolation between -50% at score 0 
    # and +15% at score 1
    base_adjustment = -50 + (current_score * 65)
    
    # Add risk levels and confidence ratings
    if current_score >= 0.8:
        risk_level = "low"
        confidence = "high"
        max_increase = 15
    elif 0.6 <= current_score < 0.8:
        risk_level = "moderate"
        confidence = "medium"
        max_increase = 10
    elif 0.4 <= current_score < 0.6:
        risk_level = "elevated"
        confidence = "medium"
        max_increase = 5
    else:
        risk_level = "high"
        confidence = "high"
        max_increase = 0
    
    # Cap positive adjustments at max_increase
    final_adjustment = min(base_adjustment, max_increase) if base_adjustment > 0 else base_adjustment
    
    return {
        "workload_adjustment": round(final_adjustment, 1),
        "risk_level": risk_level,
        "confidence": confidence,
        "recommendations": _get_workload_recommendations(current_score)
    }

def analyze_wellbeing_trend(data: List[Dict]) -> Tuple[float, str, str]:
    """
    Analyze wellbeing scores and recommend a tone of voice.
    
    Returns:
    Tuple containing (current_score, trend_description, recommended_tone)
    """
    # Filter for wellbeing entries and sort by date
    wellbeing_entries = [
        entry for entry in data 
        if entry['type'] == 'wellbeing'
    ]
    wellbeing_entries.sort(key=lambda x: x['scoreDateTime'])
    
    # Extract scores
    scores = [entry['score'] for entry in wellbeing_entries]
    
    if not scores:
        return (0, "No data available", "neutral")
    
    current_score = scores[-1]
    
    # Calculate trend
    if len(scores) > 1:
        avg_previous = sum(scores[:-1]) / len(scores[:-1])
        score_change = current_score - avg_previous
        
        # Define thresholds for significant changes
        SIGNIFICANT_CHANGE = 0.05
        
        if score_change > SIGNIFICANT_CHANGE:
            trend = "improving"
        elif score_change < -SIGNIFICANT_CHANGE:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient data"
    
    # Determine tone based on current score and trend
    if current_score >= 0.8:
        if trend == "improving":
            tone = "enthusiastic and encouraging"
        else:
            tone = "positive and supportive"
    elif 0.6 <= current_score < 0.8:
        if trend == "improving":
            tone = "optimistic and motivating"
        elif trend == "declining":
            tone = "gentle and guiding"
        else:
            tone = "balanced and constructive"
    else:
        if trend == "improving":
            tone = "encouraging and supportive"
        elif trend == "declining":
            tone = "empathetic and caring"
        else:
            tone = "understanding and helpful"
            
    trend_description = f"Score is {trend} with current wellbeing at {current_score:.2f}"
    
    return (current_score, trend_description, tone)

def _get_workload_recommendations(score: float) -> List[str]:
    """
    Provide specific workload recommendations based on the score
    """
    recommendations = []
    
    if score >= 0.8:
        recommendations.extend([
            "Consider taking on additional challenging projects",
            "Good time for learning new skills",
            "Can handle increased responsibility",
            "Monitor for signs of overextension"
        ])
    elif 0.6 <= score < 0.8:
        recommendations.extend([
            "Maintain current workload",
            "Focus on optimization and efficiency",
            "Build in buffer for unexpected tasks",
            "Regular check-ins to monitor energy levels"
        ])
    elif 0.4 <= score < 0.6:
        recommendations.extend([
            "Prioritize essential tasks only",
            "Delegate non-critical work",
            "Schedule regular breaks",
            "Review and postpone non-urgent commitments"
        ])
    else:
        recommendations.extend([
            "Significant workload reduction needed",
            "Focus only on critical tasks",
            "Seek additional support and resources",
            "Consider short-term adjustments to responsibilities"
        ])
    
    return recommendations

def main(json_data: List[Dict], current_score: float) -> Dict:
    """
    Process wellbeing data and return recommendations by comparing current score
    against historical data.
    
    Args:
        json_data: List of dictionary entries containing historical wellbeing data
        current_score: Float between 0 and 1 representing current wellbeing score
        
    Returns:
        Dictionary containing analysis and recommendations
    """
    # Validate score is between 0 and 1
    if not 0 <= current_score <= 1:
        raise ValueError("Current score must be between 0 and 1")
    
    # Filter and sort historical wellbeing entries
    wellbeing_entries = [
        entry for entry in json_data 
        if entry['type'] == 'wellbeing'
    ]
    wellbeing_entries.sort(key=lambda x: x['scoreDateTime'])
    
    # Extract historical scores
    historical_scores = [entry['score'] for entry in wellbeing_entries]
    
    if not historical_scores:
        trend = "insufficient historical data"
        avg_previous = None
    else:
        avg_previous = sum(historical_scores) / len(historical_scores)
        score_change = current_score - avg_previous
        
        # Define thresholds for significant changes
        SIGNIFICANT_CHANGE = 0.05
        
        if score_change > SIGNIFICANT_CHANGE:
            trend = "improving"
        elif score_change < -SIGNIFICANT_CHANGE:
            trend = "declining"
        else:
            trend = "stable"
    
    # Determine tone based on current score and trend
    if current_score >= 0.8:
        if trend == "improving":
            tone = "enthusiastic and encouraging"
        else:
            tone = "positive and supportive"
    elif 0.6 <= current_score < 0.8:
        if trend == "improving":
            tone = "optimistic and motivating"
        elif trend == "declining":
            tone = "gentle and guiding"
        else:
            tone = "balanced and constructive"
    else:
        if trend == "improving":
            tone = "encouraging and supportive"
        elif trend == "declining":
            tone = "empathetic and caring"
        else:
            tone = "understanding and helpful"
    
    # Create trend description
    if avg_previous is not None:
        trend_description = (
            f"Score is {trend} from historical average of {avg_previous:.2f} "
            f"to current wellbeing at {current_score:.2f}"
        )
    else:
        trend_description = (
            f"Current wellbeing at {current_score:.2f}, "
            f"insufficient historical data for trend analysis"
        )
    
    workload_analysis = calculate_workload_capacity(current_score)
    
    return {
        "current_wellbeing_score": current_score,
        "historical_average": avg_previous,
        "trend_analysis": trend_description,
        "recommended_tone": tone,
        "workload_capacity": workload_analysis,
        "detailed_recommendations": {
            "communication_style": tone,
            "suggested_approach": _get_approach_suggestions(current_score),
        }
    }

def _get_approach_suggestions(score: float) -> str:
    """
    Provide specific approach suggestions based on the score
    """
    if score >= 0.8:
        return "Focus on maintaining positive momentum and celebrating achievements"
    elif 0.6 <= score < 0.8:
        return "Balance encouragement with practical guidance for improvement"
    else:
        return "Emphasize support and gentle encouragement while offering concrete help"