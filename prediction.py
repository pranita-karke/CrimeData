import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sqlite3

def get_db_connection(db_file='crime_data.db'):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def train_and_predict(target_year, province=None, district=None):
    """
    Trains a model on historical data and predicts crime for the target year.
    Returns a dictionary with prediction details.
    """
    conn = get_db_connection()
    try:
        query = "SELECT year, crime_type, total_cases FROM main_crime WHERE 1=1"
        params = []
        
        if province:
            query += " AND TRIM(province) = ? COLLATE NOCASE"
            params.append(province.strip())
        if district:
            # Use LIKE to match "Kathmandu" against "Kathmandu Metropolitan", etc.
            query += " AND district LIKE ? COLLATE NOCASE"
            params.append(f"{district.strip()}%")
            
        df = pd.read_sql_query(query, conn, params=params)
        
        if df.empty:
            return {"error": "No data found for the selected location"}

        # Convert year to integer (handle potential string formatting)
        # Assuming year is like '2078/079' or '2078', we need a consistent integer representation.
        # Let's check the data format. Based on previous context, it might be strings.
        # For simple regression, we can use the first 4 digits if it's a fiscal year string.
        
        # Helper to parse year
        def parse_year(y):
            s = str(y).strip()
            if '/' in s:
                return int(s.split('/')[0]) # Take start of fiscal year
            try:
                return int(s)
            except:
                return 0

        df['year_int'] = df['year'].apply(parse_year)
        df = df[df['year_int'] > 0] # Filter invalid years
        
        target_year_int = int(target_year)
        
        results = []
        crime_types = df['crime_type'].unique()
        
        for c_type in crime_types:
            sub_df = df[df['crime_type'] == c_type].groupby('year_int')['total_cases'].sum().reset_index()
            
            if len(sub_df) < 2:
                # Not enough points for regression, use last known value or 0
                predicted_val = sub_df['total_cases'].iloc[-1] if not sub_df.empty else 0
                trend = 0
            else:
                X = sub_df[['year_int']]
                y = sub_df['total_cases']
                
                # Weighted Linear Regression (Give more weight to recent years)
                # Weights: 1.0 for oldest, increasing by 0.2 per year
                sample_weights = np.linspace(1, 2, len(sub_df))
                
                model = LinearRegression()
                model.fit(X, y, sample_weight=sample_weights)
                
                # Predict
                raw_prediction = model.predict([[target_year_int]])[0]
                
                # Amplify Trend for Future Years (User requested "more changes")
                # If projecting far out, add a small compound factor based on slope
                years_ahead = target_year_int - sub_df['year_int'].max()
                if years_ahead > 0:
                    slope = model.coef_[0]
                    # Add 10% acceleration to the slope per year ahead to differentiate years more
                    raw_prediction += (slope * 0.1 * years_ahead)

                predicted_val = max(0, raw_prediction)
                
                # Calculate trend (slope)
                trend = model.coef_[0]
            
            results.append({
                'crime_type': c_type,
                'predicted_cases': round(predicted_val),
                'trend': trend
            })
            
        # Analysis
        results.sort(key=lambda x: x['predicted_cases'], reverse=True)
        total_predicted = sum(r['predicted_cases'] for r in results)
        
        # Filter rising crimes with a significant trend
        # Threshold: Trend must be > 0.5 cases per year to be considered "Highlighted"
        rising_crimes = [r for r in results if r['trend'] > 0.5]
        rising_crimes.sort(key=lambda x: x['trend'], reverse=True) # Sort by steepest increase
        
        # Determine Safety Level based on comparison with the LAST KNOWN YEAR
        last_year = df['year_int'].max()
        last_year_total = df[df['year_int'] == last_year]['total_cases'].sum()
        
        safety_status = "Stable"
        
        # Logic: 
        # 1. High Risk = Rising Trend AND Significant Volume (> 10 cases)
        # 2. Rising (Low Vol) = Rising Trend but low volume
        # 3. Improving = Declining Trend
        
        if total_predicted > last_year_total * 1.02: # Rising > 2%
            if total_predicted > 10:
                safety_status = "High Risk (Rising Trend)"
            else:
                safety_status = "Stable (Low Volume)"
        elif total_predicted < last_year_total * 0.98:
            safety_status = "Improving (Declining Trend)"
            
        # Fallback: If High Risk but no rising crimes shown (due to low volume), force show the top increasing one
        if safety_status == "High Risk (Rising)" and not rising_crimes:
            any_rising = [r for r in results if r['trend'] > 0]
            if any_rising:
                any_rising.sort(key=lambda x: x['trend'], reverse=True)
                rising_crimes = [any_rising[0]]

        # --- Synthetic Alerts (Requested by User) ---
        if district:
            d_norm = district.strip().lower()
            
            # 1. Theft / Major Urban Poverty Areas
            THEFT_DISTRICTS = [
                'kathmandu', 'lalitpur', 'bhaktapur', 'kaski', 'morang', 'sunsari', 
                'parsa', 'rupandehi', 'chitwan', 'banke', 'dhanusha'
            ]
            # Check for partial match (e.g. "kathmandu" matches "kathmandu metropolitan")
            if any(t in d_norm for t in THEFT_DISTRICTS):
                rising_crimes.append({
                    'crime_type': 'Theft (High Risk Area)', 
                    'predicted_cases': 150, # Dummy high val
                    'trend': 15.0 
                })

            # 2. Drug Abuse (Refined Logic)
            # A. Key Border Transit Points (High Trafficking Risk)
            BORDER_HUBS = [
                'jhapa', 'morang', 'parsa', 'rupandehi', 'banke', 'kailali', 'kanchanpur'
            ]
            
            # B. High Illiteracy / Low HDI Districts (Vulnerable Populations)
            # Focused on Prov 2 (Madhesh) and Karnali/Sudurpaschim remote areas
            VULNERABLE_DISTRICTS = [
                'rautahat', 'mahottari', 'sarlahi', 'dhanusha', 'bara', 'siraha', 'saptari', # Madhesh
                'humla', 'bajura', 'kalikot', 'mugu', 'dolpa', 'achham', 'bajhang' # Remote Hills
            ]

            is_border = any(d in d_norm for d in BORDER_HUBS)
            is_vulnerable = any(d in d_norm for d in VULNERABLE_DISTRICTS)

            if is_border:
                rising_crimes.append({
                    'crime_type': 'Drug Abuse (Border Transit Risk)', 
                    'predicted_cases': 140, 
                    'trend': 18.5
                })
            elif is_vulnerable:
                 rising_crimes.append({
                    'crime_type': 'Drug Abuse (High Vulnerability)', 
                    'predicted_cases': 90, 
                    'trend': 8.5
                })
            
            # Re-sort to show most critical top
            rising_crimes.sort(key=lambda x: x['trend'], reverse=True)
            
        return {
            'target_year': target_year,
            'total_predicted_cases': round(total_predicted),
            'safety_status': safety_status,
            'rising_crimes': rising_crimes[:5], # Top 5 rising
            'detailed_predictions': results
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    finally:
        conn.close()
