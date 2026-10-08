# project: genai_fraud_detection
# app: genai_app

import os
import io
import base64
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
import google.generativeai as genai

# 🚫 Temporary local fallback logic instead of missing utils modules

def train_gan(df):
    return "✅ GAN training completed (mock)"

def train_vae(df):
    return "✅ VAE training completed (mock)"

def train_hybrid(df):
    return "✅ Hybrid model training completed (mock)"

def train_classifier(df):
    return "✅ Classifier trained (mock)"

def predict_transaction(data):
    # Mock logic for fraud detection
    if data['amount'] > 10000 or "vpn" in data['ip'].lower():
        return "⚠️ Potential Fraudulent Transaction"
    return "✅ Transaction appears safe"

# ✅ Configure Gemini with API Key and model
GEMINI_MODEL = "gemini-1.5-pro"
genai.configure(api_key="AIzaSyAysVqWZ-Ydq8NTcPZN6QwpVX5JkEDE17Q")

#  Home Page
def UserHome(request):
    return render(request, 'users/UserHome.html')
def base(request):
    return render(request, 'base.html')

#  Registration
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ' Registration successful.')
            return render(request, 'UserRegistration.html')
        else:
            messages.error(request, '❌ Email or Mobile already exists.')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistration.html', {'form': form})

# 🔐 Login
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('password')
        try:
            user = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if user.status == "activated":
                request.session['id'] = user.id
                request.session['loggeduser'] = user.name
                return redirect('UserHome')
            else:
                messages.error(request, 'Your account is not activated.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login ID or Password')
    return render(request, 'UserLogin.html')

# 📊 Dataset Analysis + Gemini Summary

def analyse_dataset(request):
    context = {}
    file_path = os.path.join(settings.MEDIA_ROOT, 'transactions.csv')
    if not os.path.exists(file_path):
        messages.error(request, "Dataset not found.")
        return render(request, 'users/analyse.html', context)

    try:
        df = pd.read_csv(file_path)
        context['shape'] = df.shape
        context['describe_html'] = df.describe(include='all').fillna('').to_html(classes='table table-bordered')

        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        stream = io.BytesIO()
        fig.savefig(stream, format='png')
        stream.seek(0)
        context['heatmap'] = base64.b64encode(stream.read()).decode('utf-8')

        prompt = f"""
You are a fraud analytics expert. Based on the below transaction data:
1. Identify common e-commerce fraud patterns
2. Suggest AI models suitable for real-time detection (GAN, VAE, Hybrid)
3. Analyze any ethical risks or biases

Sample:
{df[['amount','payment_method','location','is_fraud']].head(10).to_csv(index=False)}
        """
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        context['ai_insight'] = response.text

    except Exception as e:
        messages.error(request, f"Error: {e}")
    return render(request, 'users/analyse.html', context)

# 🤖 Train Models (GAN, VAE, Hybrid)
def train_models(request):
    context = {}
    file_path = os.path.join(settings.MEDIA_ROOT, 'transactions.csv')
    if not os.path.exists(file_path):
        messages.error(request, "Dataset not found.")
        return render(request, 'users/train.html', context)

    try:
        df = pd.read_csv(file_path)
        results = {}
        results['gan'] = train_gan(df)
        results['vae'] = train_vae(df)
        results['hybrid'] = train_hybrid(df)
        context['results'] = results
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return render(request, 'users/train.html', context)

# 🧪 Predict Fraud

def predict_fraud(request):
    context = {}
    if request.method == 'POST':
        try:
            data = {
                'amount': float(request.POST['amount']),
                'method': request.POST['method'],
                'location': request.POST['location'],
                'ip': request.POST['ip']
            }
            prediction = predict_transaction(data)
            context['prediction'] = prediction
            context['input_data'] = data
        except Exception as e:
            messages.error(request, f"Prediction Error: {e}")
    return render(request, 'users/predict.html', context)
