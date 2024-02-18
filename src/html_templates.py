css = """<style>
/* Base styles for chat messages */
.chat-message {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
}

/* Avatar styling */
.chat-message .avatar img {
    border-radius: 50%;
    max-height: 78px;
    max-width: 78px;
    object-fit: cover;
    margin-right: 10px;
}

/* Message bubble styling */
.chat-message .message {
    padding: 10px;
    border-radius: 15px;
    font-size: 16px;
    line-height: 1.5;
}

/* Bot message styling */
.bot .message {
    background-color: #e0e0e0;
    color: #333;
}

/* User message styling */
.user .message {
    background-color: #007bff;
    color: #fff;
    text-align: right;
}

/* Responsive design adjustments */
@media screen and (max-width: 768px) {
    .chat-message {
        flex-direction: column;
        align-items: flex-start;
    }

    .chat-message .avatar img {
        margin-bottom: 5px;
    }
}
</style>
"""

bot_template = """
<div class="chat-message bot">
    <div class="avatar">
        <img src="" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
"""

user_template = """
<div class="chat-message user">
    <div class="avatar">
        <img src="">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
"""
