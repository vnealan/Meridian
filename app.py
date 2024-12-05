from flask import Flask, request, jsonify
import json
from typing import Dict, Any
from app_pipeline import generate_health_recommendation
import time

app = Flask(__name__)


def format_meal_plan_html(meal_plan: str) -> str:
    """Convert the meal plan text into formatted HTML."""
    html = ['<div class="updated-plan">']
    
    # Split the plan into sections
    sections = meal_plan.split('\n\n')
    
    for section in sections:
        if not section.strip():
            continue
        section = section.replace('\n', '')
        if section.startswith('Updated Meal Plan'):
            html.append(f'<h2 class="plan-title">{section}</h2>')
            continue
            
        # Handle meal sections
        if any(meal in section for meal in ['Breakfast', 'Lunch', 'Dinner', 'Snack']):
            html.append('<div class="meal-section">')
            
            # Split into title and content
            parts = section.split(':\\n-')
            if len(parts) > 0:
                title = parts[0]
                html.append(f'<h3 class="meal-title">{title}</h3>')
                
                if len(parts) > 1:
                    items = parts[1].split('\\n-')
                    items = [item.replace('\\n','') for item in items]
                    html.append('<ul class="meal-items">')
                    for item in items:
                        if item.strip():
                            print(item)
                            # Highlight recommendations
                            if 'Add' in item or 'Incorporate' in item:
                                html.append(f'<li class="recommendation">{item.strip()}</li>')
                            else:
                                html.append(f'<li>{item.strip()}</li>')
                    html.append('</ul>')
                
            html.append('</div>')
            
        # Handle supplements
        elif 'Magnesium' in section or 'Supplement' in section:
            html.append('<div class="supplements-section">')
            items = section.split('\\n-')
            for item in items:
                if item.strip():
                    html.append(f'<div class="supplement-item">{item.strip()}</div>')
            html.append('</div>')
    
    html.append('</div>')
    return '\n'.join(html)

def read_html_file(filepath: str) -> str:
    """Read HTML content from file."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return f"<p>Error loading HTML content: {str(e)}</p>"

def run_pipeline(value: float) -> Dict[str, Any]:
    """
    Process the input value through various pipeline steps.
    """
    try:
        results = generate_health_recommendation(value/100)
        results = format_meal_plan_html(results)
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise Exception(f"Pipeline error: {str(e)}")

@app.route('/process', methods=['POST'])
def process_value():
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        results = run_pipeline(value)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400

@app.route('/', methods=['GET'])
def home():
    meal_plan_html = read_html_file('/Users/nealan/Documents/prototypes/health-hackathon/base_meal_plan.html')
    
    return f'''
    <html>
        <head>
            <title>Health Plan Dashboard</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Inter', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f7fa;
                    color: #1a1a1a;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }}
                .controls {{
                    background-color: #ffffff;
                    padding: 2rem;
                    border-radius: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-top: 2rem;
                }}
                .slider-container {{
                    margin: 1.5rem 0;
                }}
                .slider {{
                    width: 100%;
                    height: 8px;
                    -webkit-appearance: none;
                    background: #e9ecef;
                    border-radius: 4px;
                    outline: none;
                }}
                .slider::-webkit-slider-thumb {{
                    -webkit-appearance: none;
                    width: 20px;
                    height: 20px;
                    background: #3498db;
                    border-radius: 50%;
                    cursor: pointer;
                    transition: background .15s ease-in-out;
                }}
                .slider::-webkit-slider-thumb:hover {{
                    background: #2980b9;
                }}
                .value-display {{
                    font-size: 1.5rem;
                    color: #2c3e50;
                    text-align: center;
                    margin: 1rem 0;
                }}
                .pipeline-steps {{
                    display: flex;
                    justify-content: space-between;
                    margin: 2rem 0;
                    padding: 0;
                }}
                .step {{
                    flex: 1;
                    margin: 0 0.5rem;
                    padding: 1rem;
                    background: #ffffff;
                    border-radius: 8px;
                    text-align: center;
                    transition: all 0.3s ease;
                }}
                .step.active {{
                    background: #e3f2fd;
                    border-color: #2196f3;
                }}
                .step.completed {{
                    background: #e8f5e9;
                    border-color: #4caf50;
                }}
                .step.error {{
                    background: #ffebee;
                    border-color: #f44336;
                }}
                #result {{
                    background-color: #ffffff;
                    padding: 1.5rem;
                    border-radius: 8px;
                    margin-top: 2rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .processing {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 1rem;
                    background-color: #e3f2fd;
                    border-radius: 8px;
                    margin: 1rem 0;
                }}
                .processing-spinner {{
                    width: 24px;
                    height: 24px;
                    border: 3px solid #bbdefb;
                    border-top: 3px solid #2196f3;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-right: 1rem;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {meal_plan_html}

                <div class="controls">
                    <h2>Adjustment Controls</h2>
                    <div class="slider-container">
                        <label for="valueSlider">Adjust Plan Intensity:</label><br>
                        <input type="range" 
                               id="valueSlider" 
                               class="slider" 
                               min="0" 
                               max="100" 
                               step="0.1" 
                               value="50">
                    </div>
                    
                    <div class="value-display">
                        Current Value: <span id="currentValue">50.0</span>
                    </div>
                    
                    <div class="processing" style="display: none;">
                        <div class="processing-spinner"></div>
                        <span class="processing-text">Processing...</span>
                    </div>

                    <div class="pipeline-steps">
                        <div class="step" id="step-input">
                            <strong>Input Validation</strong>
                        </div>
                        <div class="step" id="step-process">
                            <strong>Processing</strong>
                        </div>
                        <div class="step" id="step-generate">
                            <strong>Generating Plan</strong>
                        </div>
                        <div class="step" id="step-complete">
                            <strong>Completing</strong>
                        </div>
                    </div>
                    
                    <div id="result">
                        Results will appear here...
                    </div>
                </div>
            </div>
            
            <script>
                const slider = document.getElementById('valueSlider');
                const currentValue = document.getElementById('currentValue');
                const resultDiv = document.getElementById('result');
                const processingDiv = document.querySelector('.processing');
                
                function updateStep(stepId, status) {{
                    const step = document.getElementById(stepId);
                    step.classList.remove('active', 'completed', 'error');
                    step.classList.add(status);
                }}

                function resetSteps() {{
                    const steps = document.querySelectorAll('.step');
                    steps.forEach(step => {{
                        step.classList.remove('active', 'completed', 'error');
                    }});
                }}

                let processingTimeout;
                
                async function processValue(value) {{
                    try {{
                        resetSteps();
                        processingDiv.style.display = 'flex';
                        resultDiv.innerHTML = 'Processing...';
                        
                        updateStep('step-input', 'active');
                        await new Promise(resolve => setTimeout(resolve, 500));
                        updateStep('step-input', 'completed');
                        
                        updateStep('step-process', 'active');
                        await new Promise(resolve => setTimeout(resolve, 500));
                        updateStep('step-process', 'completed');
                        
                        updateStep('step-generate', 'active');
                        
                        const response = await fetch('/process', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: JSON.stringify({{ value: parseFloat(value) }})
                        }});
                        
                        updateStep('step-generate', 'completed');
                        updateStep('step-complete', 'active');
                        
                        const data = await response.json();
                        
                        if (data.status === 'success') {{
                            updateStep('step-complete', 'completed');
                            resultDiv.innerHTML = '<h3>Results:</h3>' + 
                                                '<pre>' + JSON.stringify(data.results, null, 2) + '</pre>';
                        }} else {{
                            updateStep('step-complete', 'error');
                            resultDiv.innerHTML = '<h3>Error:</h3>' + 
                                                '<pre style="color: red;">' + data.error + '</pre>';
                        }}
                    }} catch (error) {{
                        updateStep('step-complete', 'error');
                        resultDiv.innerHTML = '<h3>Error:</h3>' + 
                                            '<pre style="color: red;">' + error.message + '</pre>';
                    }} finally {{
                        processingDiv.style.display = 'none';
                    }}
                }}
                
                // Debounce the slider input to prevent too many requests
                slider.oninput = function() {{
                    currentValue.textContent = parseFloat(this.value).toFixed(1);
                    clearTimeout(processingTimeout);
                    processingTimeout = setTimeout(() => {{
                        processValue(this.value);
                    }}, 300);
                }}
                
                // Process initial value
                processValue(slider.value);
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5000)