import os

file_path = r'c:\Users\USER\Documents\LoanMate\templates\accounts\register.html'

content = """{% extends 'base.html' %}

{% block title %}Register | LoanMate{% endblock %}

{% block content %}
<div style="max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
    <h2>Register</h2>

    {% if errors %}
    <ul style="color: red; list-style: none; padding: 0;">
        {% for error in errors %}
        <li>{{ error }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        <div style="margin-bottom: 15px;">
            <label>Username</label><br>
            <input type="text" name="username" value="{{ data.username }}" required style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Email (Optional)</label><br>
            <input type="email" name="email" value="{{ data.email }}" style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Password</label><br>
            <input type="password" name="password" required style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Confirm Password</label><br>
            <input type="password" name="confirm_password" required style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Role</label><br>
            <select name="role" style="width: 100%; padding: 8px;">
                <option value="user" {% if data.role == 'user' %}selected{% endif %}>User (Borrower)</option>
                <option value="officer" {% if data.role == 'officer' %}selected{% endif %}>Officer (Lender)</option>
            </select>
        </div>
        <button type="submit"
            style="width: 100%; padding: 10px; background-color: #007bff; color: white; border: none; cursor: pointer;">Register</button>
    </form>

    <p style="margin-top: 15px; text-align: center;">
        Already have an account? <a href="{% url 'accounts:login' %}">Login</a>
    </p>
</div>
{% endblock %}
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully overwrote register.html with correct content.")
