import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from core.models import load_models
from core.helper import t

models=load_models()
classifier=models['heart']

# Load nutrition database from CSV file
@st.cache_data
def load_nutrition_data():
    try:
        data = pd.read_csv("C:/Users/New/Downloads/CDPrediction_Modularized/CDPrediction/data/Indian_Food_Nutrition_Processed.csv")

        # Required columns excluding 'Category'
        required_columns = [
            "Dish Name", "Calories (kcal)", "Carbohydrates (g)", 
            "Protein (g)", "Fats (g)", "Free Sugar (g)", "Fibre (g)", 
            "Sodium (mg)"
        ]

        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            st.warning(f"CSV file is missing required columns: {missing_cols}. Using backup database.")
            return load_backup_nutrition_data()

        # Add Category if not present
        if "Category" not in data.columns:
            data["Category"] = "Other"
            data.loc[data["Dish Name"].str.contains("tea|coffee|juice|water", case=False), "Category"] = "Beverages"
            data.loc[data["Dish Name"].str.contains("rice|bread|oat|wheat|grain|pasta", case=False), "Category"] = "Grains"
            data.loc[data["Dish Name"].str.contains("chicken|fish|meat|beef|lamb|egg|tofu|bean", case=False), "Category"] = "Proteins"
            data.loc[data["Dish Name"].str.contains("spinach|tomato|carrot|vegetable|broccoli", case=False), "Category"] = "Vegetables"
            data.loc[data["Dish Name"].str.contains("apple|orange|banana|fruit|berry", case=False), "Category"] = "Fruits"
            data.loc[data["Dish Name"].str.contains("almond|walnut|cashew|peanut", case=False), "Category"] = "Nuts"
            data.loc[data["Dish Name"].str.contains("oil|butter|ghee", case=False), "Category"] = "Fats"
            data.loc[data["Dish Name"].str.contains("milk|yogurt|curd|cheese", case=False), "Category"] = "Dairy"

        return data

    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.warning("Nutrition database CSV file not found or empty. Using backup database.")
        return load_backup_nutrition_data()


# Backup nutrition database with sample data
def load_backup_nutrition_data():
    data = {
        "Dish Name": ["Hot tea (Garam Chai)", "Instant coffee", "Espreso coffee", 
                     "Oatmeal", "Whole grain bread", "Brown rice", "Salmon", 
                     "Chicken breast", "Lentils", "Tofu", "Spinach", "Broccoli", 
                     "Carrots", "Apples", "Berries", "Almonds", "Walnuts", 
                     "Olive oil", "Yogurt", "Cottage cheese"],
        "Calories (kcal)": [16.14, 23.16, 51.54, 150, 80, 112, 208, 165, 116, 94, 23, 31, 41, 52, 42, 164, 185, 119, 59, 98],
        "Carbohydrates (g)": [2.58, 3.65, 6.62, 27, 15, 24, 0, 0, 20, 2, 3.6, 6, 10, 14, 11, 6, 4, 0, 3.6, 3.4],
        "Protein (g)": [0.39, 0.64, 1.75, 5, 3, 2.5, 20, 31, 9, 10, 2.9, 2.6, 0.9, 0.3, 0.7, 6, 4.3, 0, 10, 11.1],
        "Fats (g)": [0.53, 0.75, 2.14, 2.5, 1, 0.9, 13, 3.6, 0.4, 6, 0.4, 0.3, 0.2, 0.2, 0.4, 14, 18.5, 14, 0.4, 4.3],
        "Free Sugar (g)": [2.58, 3.62, 6.53, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10.4, 4, 0, 0, 0, 0, 0],
        "Fibre (g)": [0, 0, 0, 4, 2, 1.8, 0, 0, 7.9, 1.6, 2.2, 2.6, 2.8, 2.4, 2, 3.5, 1.9, 0, 0, 0],
        "Sodium (mg)": [3.12, 4.92, 13.98, 2, 137, 5, 59, 74, 2, 7, 79, 33, 69, 1, 1, 0, 1, 0, 50, 380],
        "Calcium (mg)": [14.2, 20.87, 58.1, 54, 26, 10, 13, 15, 37, 350, 99, 47, 33, 6, 12, 75, 28, 1, 183, 83],
        "Iron (mg)": [0.02, 0.06, 0.15, 1.7, 0.9, 0.5, 0.3, 1, 3.3, 2, 2.7, 0.7, 0.3, 0.1, 0.4, 1.1, 0.8, 0.1, 0.1, 0.1],
        "Vitamin C (mg)": [0.5, 1.51, 1.51, 0, 0, 0, 0, 0, 3, 0, 28, 89, 5, 4.6, 9.7, 0, 0.4, 0, 0, 0],
        "Folate (µg)": [1.8, 5.6, 5.53, 32, 27, 8, 26, 4, 181, 19, 194, 63, 19, 3, 24, 14, 28, 0, 12, 12],
        "Category": ["Beverages", "Beverages", "Beverages", 
                    "Grains", "Grains", "Grains", "Proteins", 
                    "Proteins", "Proteins", "Proteins", "Vegetables", "Vegetables", 
                    "Vegetables", "Fruits", "Fruits", "Nuts", "Nuts", 
                    "Fats", "Dairy", "Dairy"]
    }
    return pd.DataFrame(data)

# Heart-healthy diet guidelines based on NCI standards
def get_heart_healthy_guidelines(age, gender, bmi, activity_level, risk_level):
    """Calculate daily nutritional requirements based on patient parameters"""
    # Base calorie calculation
    if gender == "Male":
        base_calories = 10 * 70 + 6.25 * 175 - 5 * age + 5  # Mifflin-St Jeor equation for men
    else:
        base_calories = 10 * 60 + 6.25 * 163 - 5 * age - 161  # Mifflin-St Jeor equation for women
    
    # Activity factor
    activity_factors = {
        "Sedentary": 1.2,
        "Lightly active": 1.375,
        "Moderately active": 1.55,
        "Very active": 1.725,
        "Extremely active": 1.9
    }
    
    # Calculate daily calorie needs
    daily_calories = base_calories * activity_factors[activity_level]
    
    # Adjust calories based on risk level and BMI
    if risk_level > 0.7:  # High risk
        if bmi > 25:
            daily_calories *= 0.85  # 15% calorie reduction for weight loss
        sodium_limit = 1500  # mg - stricter sodium for high risk
    else:  # Lower risk
        if bmi > 25:
            daily_calories *= 0.9  # 10% calorie reduction for weight loss
        sodium_limit = 2300  # mg - standard sodium recommendation
    
    # Calculate macronutrient distribution for heart health
    carbs_percent = 0.55  # 55% of calories from carbs
    protein_percent = 0.20  # 20% of calories from protein
    fat_percent = 0.25  # 25% of calories from fat
    
    carbs_calories = daily_calories * carbs_percent
    protein_calories = daily_calories * protein_percent
    fat_calories = daily_calories * fat_percent
    
    carbs_grams = carbs_calories / 4  # 4 calories per gram of carbs
    protein_grams = protein_calories / 4  # 4 calories per gram of protein
    fat_grams = fat_calories / 9  # 9 calories per gram of fat
    
    # Additional heart-healthy nutrient targets
    fiber_target = 25 if gender == "Female" else 38  # g/day
    sugar_limit = 25 if gender == "Female" else 36  # g/day
    
    guidelines = {
        "daily_calories": round(daily_calories),
        "carbs_grams": round(carbs_grams),
        "protein_grams": round(protein_grams),
        "fat_grams": round(fat_grams),
        "sodium_limit": sodium_limit,
        "fiber_target": fiber_target,
        "sugar_limit": sugar_limit
    }
    
    return guidelines

# Generate meal plan based on nutritional requirements
def generate_meal_plan(nutrition_db, guidelines, risk_level, days=1):
    """Generate a 1-day meal plan based on nutritional guidelines"""
    meal_plan = {}
    
    # Define meal structure
    meal_structure = {
        "Breakfast": {"Calories": 0.25, "Grains": 1, "Fruits": 1, "Dairy": 1, "Proteins": 0},
        "Lunch": {"Calories": 0.35, "Grains": 1, "Vegetables": 2, "Proteins": 1, "Fats": 1},
        "Dinner": {"Calories": 0.30, "Grains": 1, "Vegetables": 2, "Proteins": 1, "Fats": 1},
        "Snacks": {"Calories": 0.10, "Fruits": 1, "Nuts": 1, "Dairy": 0}
    }
    
    # Food preferences based on risk level
    preferred_foods = {}
    avoid_foods = []
    
    if risk_level > 0.7:  # High risk
        preferred_foods = {
            "Grains": ["Oatmeal", "Whole grain bread", "Brown rice"],
            "Proteins": ["Salmon", "Tofu", "Lentils"],
            "Fats": ["Olive oil"]
        }
        avoid_foods = ["Instant coffee", "Espreso coffee"]  # High caffeine
    else:  # Lower risk
        preferred_foods = {
            "Grains": ["Oatmeal", "Whole grain bread", "Brown rice"],
            "Proteins": ["Salmon", "Chicken breast", "Lentils", "Tofu"]
        }
    
    # Generate meal plan for each day
    for day in range(1, days+1):
        day_plan = {}
        day_calories = 0
        day_nutrients = {"Carbohydrates (g)": 0, "Protein (g)": 0, "Fats (g)": 0, 
                         "Sodium (mg)": 0, "Fiber (g)": 0, "Sugar (g)": 0}
        
        # For each meal of the day
        for meal, structure in meal_structure.items():
            meal_items = []
            meal_target_calories = guidelines["daily_calories"] * structure["Calories"]
            meal_calories = 0
            
            # Add food from each required category
            for category, count in structure.items():
                if category == "Calories":
                    continue
                
                # Filter foods by category
                category_foods = nutrition_db[nutrition_db["Category"] == category]
                
                # Apply preferences/restrictions
                if category in preferred_foods:
                    preferred_items = category_foods[category_foods["Dish Name"].isin(preferred_foods[category])]
                    if not preferred_items.empty:
                        category_foods = preferred_items
                
                # Remove foods to avoid
                category_foods = category_foods[~category_foods["Dish Name"].isin(avoid_foods)]
                
                if category_foods.empty:
                    continue
                
                # Select foods for this category
                for _ in range(count):
                    # If we're already over calorie target, break
                    if meal_calories >= meal_target_calories:
                        break
                    
                    # Pick a random food from this category
                    food = category_foods.sample(1).iloc[0]
                    
                    # Calculate portion to meet calorie target
                    remaining_calories = meal_target_calories - meal_calories
                    portion_factor = min(1.0, remaining_calories / (food["Calories (kcal)"] + 0.1))  # Avoid division by zero
                    
                    # Minimum reasonable portion
                    portion_factor = max(0.5, portion_factor)
                    
                    # Add to meal plan with gram amount
                    portion_grams = round(portion_factor * 100)  # Base portion is 100g
                    meal_items.append({
                        "food": food["Dish Name"],
                        "grams": portion_grams,
                        "calories": round(food["Calories (kcal)"] * portion_factor),
                        "carbs": round(food["Carbohydrates (g)"] * portion_factor, 1),
                        "protein": round(food["Protein (g)"] * portion_factor, 1),
                        "fat": round(food["Fats (g)"] * portion_factor, 1),
                        "sodium": round(food["Sodium (mg)"] * portion_factor),
                        "fiber": round(food.get("Fibre (g)", 0) * portion_factor, 1),
                        "sugar": round(food.get("Free Sugar (g)", 0) * portion_factor, 1)
                    })
                    
                    meal_calories += food["Calories (kcal)"] * portion_factor
                    day_calories += food["Calories (kcal)"] * portion_factor
                    day_nutrients["Carbohydrates (g)"] += food["Carbohydrates (g)"] * portion_factor
                    day_nutrients["Protein (g)"] += food["Protein (g)"] * portion_factor
                    day_nutrients["Fats (g)"] += food["Fats (g)"] * portion_factor
                    day_nutrients["Sodium (mg)"] += food["Sodium (mg)"] * portion_factor
                    day_nutrients["Fiber (g)"] += food.get("Fibre (g)", 0) * portion_factor
                    day_nutrients["Sugar (g)"] += food.get("Free Sugar (g)", 0) * portion_factor
            
            day_plan[meal] = {
                "items": meal_items,
                "total_calories": round(meal_calories)
            }
        
        # Add daily summary
        day_plan["Daily Summary"] = {
            "total_calories": round(day_calories),
            "carbs": round(day_nutrients["Carbohydrates (g)"], 1),
            "protein": round(day_nutrients["Protein (g)"], 1),
            "fat": round(day_nutrients["Fats (g)"], 1),
            "sodium": round(day_nutrients["Sodium (mg)"]),
            "fiber": round(day_nutrients["Fiber (g)"], 1),
            "sugar": round(day_nutrients["Sugar (g)"], 1)
        }
        
        meal_plan[f"Day {day}"] = day_plan
    
    return meal_plan

def display_meal_plan(meal_plan, guidelines):
    """Display the meal plan in a user-friendly format"""
    st.subheader("Your Personalized Heart-Healthy Meal Plan")
    
    st.write("### Daily Nutritional Targets")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Daily Calories", f"{guidelines['daily_calories']} kcal")
        st.metric("Carbohydrates", f"{guidelines['carbs_grams']} g")
    with col2:
        st.metric("Protein", f"{guidelines['protein_grams']} g")
        st.metric("Fat", f"{guidelines['fat_grams']} g")
    with col3:
        st.metric("Sodium Limit", f"{guidelines['sodium_limit']} mg")
        st.metric("Fiber Target", f"{guidelines['fiber_target']} g")
    
    # Get the day plan (always Day 1)
    day_plan = meal_plan["Day 1"]
    daily_summary = day_plan["Daily Summary"]
    
    # Show daily summary
    st.write("#### Daily Summary")
    summary_cols = st.columns(4)
    with summary_cols[0]:
        st.metric("Total Calories", f"{daily_summary['total_calories']} kcal")
    with summary_cols[1]:
        carb_percent = round((daily_summary['carbs'] * 4 / daily_summary['total_calories']) * 100)
        st.metric("Carbs", f"{daily_summary['carbs']} g ({carb_percent}%)")
    with summary_cols[2]:
        protein_percent = round((daily_summary['protein'] * 4 / daily_summary['total_calories']) * 100)
        st.metric("Protein", f"{daily_summary['protein']} g ({protein_percent}%)")
    with summary_cols[3]:
        fat_percent = round((daily_summary['fat'] * 9 / daily_summary['total_calories']) * 100)
        st.metric("Fat", f"{daily_summary['fat']} g ({fat_percent}%)")
    
    # Additional nutrients
    additional_cols = st.columns(3)
    with additional_cols[0]:
        sodium_status = "🟢" if daily_summary['sodium'] < guidelines['sodium_limit'] else "🔴"
        st.metric("Sodium", f"{daily_summary['sodium']} mg {sodium_status}")
    with additional_cols[1]:
        fiber_status = "🟢" if daily_summary['fiber'] >= guidelines['fiber_target'] else "🔴"
        st.metric("Fiber", f"{daily_summary['fiber']} g {fiber_status}")
    with additional_cols[2]:
        sugar_status = "🟢" if daily_summary['sugar'] <= guidelines['sugar_limit'] else "🔴"
        st.metric("Sugar", f"{daily_summary['sugar']} g {sugar_status}")
    
    # Display each meal ONCE ONLY
    for meal in ["Breakfast", "Lunch", "Dinner", "Snacks"]:
        if meal in day_plan:
            st.write(f"#### {meal} ({day_plan[meal]['total_calories']} kcal)")
            for item in day_plan[meal]["items"]:
                with st.expander(f"{item['food']} - {item['grams']} g ({item['calories']} kcal)"):
                    st.write(f"Carbs: {item['carbs']} g | Protein: {item['protein']} g | Fat: {item['fat']} g")
                    st.write(f"Sodium: {item['sodium']} mg | Fiber: {item['fiber']} g | Sugar: {item['sugar']} g")            

def heart_health_nutrition_tips(risk_level):
    """Provide heart health nutrition tips based on risk level"""
    general_tips = [
        "Limit saturated fats found in red meat, full-fat dairy products, and tropical oils",
        "Choose lean protein sources like fish, poultry, beans, and legumes",
        "Include plenty of fruits, vegetables, and whole grains in your diet",
        "Reduce sodium intake by limiting processed foods and added salt",
        "Stay hydrated by drinking plenty of water throughout the day"
    ]
    
    high_risk_tips = [
        "Aim for at least two servings of fatty fish like salmon or mackerel weekly for omega-3 fatty acids",
        "Replace salt with herbs and spices to flavor your food",
        "Consider the DASH diet approach which is specifically designed for heart health",
        "Limit alcohol consumption to moderate levels (1 drink/day for women, 2 drinks/day for men)",
        "Keep a food diary to track sodium intake and stay under 1,500mg daily"
    ]
    
    tips = general_tips
    if risk_level > 0.7:
        tips.extend(high_risk_tips)
    
    return tips

def run():
    page_title=t("❤️ Heart Disease Prediction")
    st.markdown("""
        <style>
            #MainMenu, footer {visibility: hidden;}
            .stButton>button {
                background-color: #6200EE;
                color: white;
                font-size: 18px;
                padding: 10px 30px;
                border-radius: 8px;
                border: none;
                transition: background-color 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #C2185B;
            }
            .css-1cpxqw2 edgvbvh3 {
                visibility: hidden;
            }
        </style>
    """, unsafe_allow_html=True)

    # Animated gradient title
    components.html(f"""
        <style>
            @keyframes fadeSlide {{
                0% {{opacity: 0; transform: translateY(-10px);}}
                100% {{opacity: 1; transform: translateY(0);}}
            }}
            #title {{
                font-family: 'Segoe UI', sans-serif;
                font-size: 3.5vw;
                font-weight: bold;
                text-align: center;
                margin-top: 15px;
                animation: fadeSlide 1s ease-out;
                background: linear-gradient(90deg, #FF4081, #FFCDD2);
                -webkit-background-clip: text;
                color: inherit;
                -webkit-text-fill-color: initial;
            }}
        </style>
        <div id="title">{page_title}</div>
    """, height=50)
    # Create tabs for prediction and nutrition counseling
    tab1, tab2 = st.tabs([t("Heart Disease Prediction"), t("Nutrition Counseling")])
    
    with tab1:
        # Input header
        st.markdown(t("🩺 Enter your health details below:"))

        # Input fields
        age = st.slider(t("Age"), 1, 100, 30)
        gender = st.selectbox(t("Gender"), ["Male", "Female"])
        weight = st.slider(t("Weight (kg)"), 30, 200, 65)
        height = st.slider(t("Height (cm)"), 100, 220, 170)
        ap_hi = st.slider(t("Systolic Blood Pressure (ap_hi)"), 50, 250, 120, step=10)
        ap_lo = st.slider(t("Diastolic Blood Pressure (ap_lo)"), 50, 200, 80, step=10)
        chol = st.selectbox(t("Cholesterol Level"), ["Normal", "Above Normal", "Well Above Normal"])
        gluc = st.selectbox(t("Glucose Level"), ["Normal", "Above Normal", "Well Above Normal"])
        smoke = st.selectbox(t("Do you Smoke?"), ["No", "Yes"])
        alco = st.selectbox(t("Do you Drink Alcohol?"), ["No", "Yes"])
        active = st.selectbox(t("Do you Exercise Regularly?"), ["No", "Yes"])

        # Encoding
        gender_val = 0 if gender == "Male" else 1
        cholesterol_val = 1 if chol == "Normal" else (2 if chol == "Above Normal" else 3)
        gluc_val = 1 if gluc == "Normal" else (2 if gluc == "Above Normal" else 3)
        smoke_val = 1 if smoke == "Yes" else 0
        alco_val = 1 if alco == "Yes" else 0
        active_val = 1 if active == "Yes" else 0

        # Prediction
        if st.button(t("🔍 Predict")):
            with st.spinner(t("🧠 Predicting based on your health data...")):
                prediction = classifier.predict([[age, gender_val, height, weight, ap_hi, ap_lo,
                                                cholesterol_val, gluc_val, smoke_val, alco_val, active_val]])[0]

                # Save results to session state
                st.session_state["heart_diagnosis"] = prediction
                st.session_state['risk_level']= 1.0 if prediction == 1 else 0.2
                st.session_state["heart_inputs"] = {
                        "Systolic BP": ap_hi,
                        "Diastoilic BP": ap_lo,
                        "Cholestrol": chol,
                        "Glucose": gluc,
                        "DO You Smoke": smoke,
                        "Alcoholic": alco,
                        "Do you Exercise Regularly?": active}

            if prediction == 0:
                predict_res = t("✅ No Cardiovascular Disease Detected")
                
                components.html(f"""  <!-- f-string enabled -->
                    <style>
                        .result {{
                            font-family: 'Segoe UI', sans-serif;
                            font-size: 32px;
                            font-weight: bold;
                            color: #4CAF50;
                            text-align: center;
                            margin-top: 30px;
                            animation: fadeIn 1s ease-in;
                        }}
                        @keyframes fadeIn {{
                            from {{opacity: 0;}}
                            to {{opacity: 1;}}
                        }}
                    </style>
                    <div class="result">{predict_res}</div>
                """, height=150)
            else:
                predict_res = t("❌ High Risk of Cardiovascular Disease")
                predict_subtext=t("⚠️ Please consult a Cardiologist immediately.")
                components.html(f""" 
                    <style>
                        .result {{
                            font-family: 'Segoe UI', sans-serif;
                            font-size: 30px;
                            font-weight: bold;
                            color: #D32F2F;
                            text-align: center;
                            margin-top: 30px;
                            animation: pulse 1s ease-in-out infinite alternate;
                        }}
                        .subtext {{
                            font-size: 18px;
                            font-weight: normal;
                            color: #FF7043;
                            text-align: center;
                            margin-top: 10px;
                        }}
                        @keyframes pulse {{
                            from {{transform: scale(1);}}
                            to {{transform: scale(1.05);}}
                        }}
                    </style>
                    <div class="result">{predict_res}</div>
                    <div class="subtext">{predict_subtext}</div>
                """, height=150)

    
    with tab2:
        st.header(t("Heart-Healthy Nutrition Counseling"))
        
        # Check if prediction has been run
        if 'heart_diagnosis' not in st.session_state:
            st.info(t("Please run a heart disease prediction first in the 'Heart Disease Prediction' tab."))
            return
        
        # Display risk level
        risk_level = st.session_state['risk_level']
        if risk_level > 0.7:
            risk_text = t("High Risk")
            risk_color = "red"
        elif risk_level > 0.3:
            risk_text = t("Moderate Risk")
            risk_color = "orange"
        else:
            risk_text = t("Low Risk")
            risk_color = "green"
        
        st.markdown(f"<p style='background-color:{risk_color}; color:white; padding:10px;'>Heart Disease Risk Level: {risk_text} ({risk_level:.2f})</p>", unsafe_allow_html=True)
        
        # Additional inputs for nutrition planning
        st.subheader(t("Additional Information for Personalized Nutrition"))
        
        height = st.number_input(t("Height (cm)"), min_value=120, max_value=220, value=170)
        weight = st.number_input(t("Weight (kg)"), min_value=30, max_value=200, value=70)
        bmi = weight / ((height/100) ** 2)
        st.write(f"BMI: {bmi:.1f}")
        
        activity_level = st.select_slider(
            t("Physical Activity Level"),
            options=["Sedentary", "Lightly active", "Moderately active", "Very active", "Extremely active"],
            value="Lightly active"
        )
        
        if st.button(t("Generate Meal Plan")):
            # Load nutrition database
            nutrition_db = load_nutrition_data()
            
            # Get nutritional guidelines based on patient data
            guidelines = get_heart_healthy_guidelines(
                st.session_state['patient_age'], 
                st.session_state['patient_gender'], 
                bmi, 
                activity_level, 
                risk_level
            )
            
            # Generate meal plan
            meal_plan = generate_meal_plan(nutrition_db, guidelines, risk_level)
            
            # Display meal plan
            display_meal_plan(meal_plan, guidelines)
            
            # Display heart health tips
            st.subheader(t("Heart Health Nutrition Tips"))
            tips = heart_health_nutrition_tips(risk_level)
            for i, tip in enumerate(tips):
                st.markdown(f"- {tip}")
            
            st.session_state["activity_level"] = activity_level
            st.session_state["nutrition_guidelines"] = guidelines
            st.session_state["nutrition_tips"] = tips

            
            # Disclaimer
            st.info(
                "Disclaimer: This meal plan is generated based on general guidelines and your input data. "
                "Please consult with a registered dietitian or healthcare provider for personalized "
                "nutritional advice tailored to your specific health needs."
            )

if __name__ == "__main__":
    run()