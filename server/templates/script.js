let previousQuestions = [];
let previousAnswers = [];
let qaPairs = [];
let answering = false;

function startQuestion() {
  answering = true;
  document.getElementById("submit-btn").innerText = "停止回答";
  submitQuestion();
}

function stopAnswerUpdates() {
  answering = false;
  document.getElementById("submit-btn").innerText = "提交问题";
}

function toggleQuestion() {
  if (answering) {
    stopAnswerUpdates();
  } else {
    startQuestion();
  }
}

function createChatContainer(panelHeadText, content, messageType) {
  const messageLabelClass = messageType === 'question' ? 'message-label-question' : 'message-label-answer';

  return `
    <div class="chat-container">
      <div class="chat-message">
        <div class="${messageLabelClass}">${panelHeadText}</div>
        <div class="message-content">${content}</div>
      </div>
    </div>
  `;
}

function displayPreviousQuestionsAndAnswers() {
  const md = new markdownit();
  let chatHTML = '';

  for (let i = 0; i < previousQuestions.length; i++) {
    chatHTML += createChatContainer("提问：", md.render(previousQuestions[i]), 'question');
    chatHTML += createChatContainer("回答：", md.render(previousAnswers[i]), 'answer');
  }

  chatHTML += createChatContainer("提问：", "<div id='question'></div>", 'question');
  chatHTML += createChatContainer("回答：", "<div id='answer'>正在思考您的问题请稍等</div>", 'answer');

  document.getElementById("qa-container").innerHTML = chatHTML;
}

async function submitQuestion() {
  //const url = 'http://52.53.130.54:8080';
  //const url = 'http://localhost:8080';
  const url = window.location.href;

  displayPreviousQuestionsAndAnswers();

  const md = new markdownit();
  var inputMessage = document.getElementById("input").value;
  qaPairs.push({role: 'user', content: inputMessage});

  var inputMessageMD = md.render(inputMessage);
  document.getElementById("question").innerHTML = inputMessageMD;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      group_name: 'default_group',
      messages: qaPairs,
      stream: true // Set stream to true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let firstChunk = true;
  let answerText = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
        stopAnswerUpdates();
        break;
    }

    if (!answering) {
      // Cancel the fetch request
      reader.cancel();
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    let stringWithNewlines = buffer.replace(/\}\{/g, '}\n{');
    let chunks = stringWithNewlines.split('\n');

    for (let i = 0; i < chunks.length - 1; i++) {
      const message = JSON.parse(chunks[i]);

      if (message.choices && message.choices[0].delta && message.choices[0].delta.content) {
        const content = message.choices[0].delta.content;
        if (content) {
          if (firstChunk) {
            firstChunk = false;
          }
          answerText += content;
          document.getElementById("answer").innerHTML = md.render(answerText);
        }
      }
    }

    buffer = chunks[chunks.length - 1];
  }

  previousQuestions.push(inputMessage);
  previousAnswers.push(answerText);
  qaPairs.push({role: 'assistant', content: answerText});
}

window.submitQuestion = submitQuestion;

window.addEventListener('DOMContentLoaded', (event) => {
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.addEventListener('click', toggleQuestion);
});
