const loginScreen = document.querySelector('.login-screen');
const chatScreen = document.querySelector('.chat-screen');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const usernameInput = document.getElementById('username');
const loginError = document.getElementById('login-error');
const messagesDiv = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');

let currentUser = null;

loginBtn.addEventListener('click', async () => {
  const username = usernameInput.value.trim().toLowerCase();
  if (!username) return;

  const res = await fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  });
  const data = await res.json();

  if (data.success) {
    currentUser = data.username;
    loginScreen.classList.add('hidden');
    chatScreen.classList.remove('hidden');
    loadMessages();
  } else {
    loginError.textContent = data.message || 'Login failed';
  }
});

logoutBtn.addEventListener('click', () => {
  currentUser = null;
  messagesDiv.innerHTML = '';
  usernameInput.value = '';
  loginError.textContent = '';
  chatScreen.classList.add('hidden');
  loginScreen.classList.remove('hidden');
});

chatForm.addEventListener('submit', async e => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;

  await fetch('/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: currentUser, text })
  });

  messageInput.value = '';
  loadMessages();
});

async function loadMessages() {
  const res = await fetch('/messages');
  const msgs = await res.json();

  messagesDiv.innerHTML = '';
  msgs.forEach(msg => {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(msg.username === currentUser ? 'you' : 'friend');
    msgDiv.textContent = `${msg.username}: ${msg.text}`;
    messagesDiv.appendChild(msgDiv);
  });
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
