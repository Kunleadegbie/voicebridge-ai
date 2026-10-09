
const $ = id => document.getElementById(id);

let currentId = null;
let currentSource = 'text_test';

// Voice recording
$('record').onclick = () => toggleRecording($('record'));

// Display an answer
function render(data) {
  currentId = data.interaction_id;
  currentSource = data.interaction_source;

  $('result').hidden = false;

  $('inputLabel').textContent =
    currentSource === 'voice' ? 'I heard' : 'Your question';

  $('transcript').textContent = data.transcript;
  $('answer').textContent = data.response;

  // Build badges safely without inserting untrusted text as HTML.
  const badges = $('badges');
  badges.replaceChildren();

  function addBadge(label, eligible = false) {
    const span = document.createElement('span');
    span.className = eligible ? 'badge eligible' : 'badge';
    span.textContent = label;
    badges.appendChild(span);
  }

  addBadge(data.journey || 'General');
  addBadge(`ASR: ${(data.asr_provider || 'none').toUpperCase()}`);

  if (data.asr_model_id) {
    addBadge(data.asr_model_id.split('/').pop());
  }

  addBadge(`LLM: ${(data.llm_provider || 'none').toUpperCase()}`);

  addBadge(
    data.validation_eligible
      ? 'PARTICIPANT-DECLARED'
      : 'TEST ONLY',
    Boolean(data.validation_eligible)
  );

  $('status').textContent = 'Complete';
  $('feedbackStatus').textContent = '';
  $('asrCorrect').value = '';

  refreshSummary();

  // Spoken answer playback.
  // Do not add FormData statements here.
  if (window.voiceBridgeSpeech) {
    try {
      const playback = window.voiceBridgeSpeech.onAnswer(
        data,
        $('language').value
      );

      if (playback && typeof playback.catch === 'function') {
        playback.catch(error => {
          console.error('Speech playback error:', error);
        });
      }
    } catch (error) {
      console.error('Speech playback error:', error);
    }
  }
}

// Submit a recorded voice question
async function sendAudio(blob) {
  $('status').textContent = 'Processing voice…';

  const form = new FormData();

  form.append('audio', blob, 'voice.wav');
  form.append('language', $('language').value);

  form.append(
    'session_id',
    localStorage.vbSession ||
      (localStorage.vbSession = crypto.randomUUID())
  );

  form.append(
    'real_user',
    $('participantMode').checked ? 'true' : 'false'
  );

  try {
    const response = await fetch('/voice/ask', {
      method: 'POST',
      body: form
    });

    let data;

    try {
      data = await response.json();
    } catch (error) {
      throw new Error('The server returned an unreadable response.');
    }

    if (!response.ok) {
      $('status').textContent =
        typeof data.detail === 'string'
          ? data.detail
          : 'Voice processing failed. Please contact the test coordinator.';
      return;
    }

    render(data);

  } catch (error) {
    console.error('Voice request error:', error);

    $('status').textContent =
      'The connection was interrupted before your answer could be displayed. ' +
      'Your question may still have been processed. ' +
      'Please contact the test coordinator before trying again.';
  }
}

// Developer text testing
$('textTest').onclick = async () => {
  const text = $('testText').value.trim();

  if (!text) return;

  $('status').textContent = 'Processing text test…';

  try {
    const response = await fetch('/text/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        language: $('language').value,
        session_id: 'developer-text-test'
      })
    });

    const data = await response.json();

    if (!response.ok) {
      $('status').textContent =
        typeof data.detail === 'string'
          ? data.detail
          : 'Text test failed.';
      return;
    }

    render(data);

  } catch (error) {
    console.error('Text test error:', error);

    $('status').textContent =
      'Unable to complete the text test. Please check the connection.';
  }
};

// Participant feedback
document.querySelectorAll('.feedback').forEach(button => {
  button.onclick = async () => {
    if (!currentId) return;

    const asrSelection = $('asrCorrect').value;

    if (currentSource === 'voice' && asrSelection === '') {
      $('feedbackStatus').textContent =
        'Please indicate whether VoiceBridge correctly heard your question.';
      return;
    }

    const payload = {
      interaction_id: currentId,
      understood: null,
      helpful: Number(button.dataset.score),
      asr_correct:
        currentSource === 'voice'
          ? asrSelection === 'true'
          : null
    };

    try {
      const response = await fetch('/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      $('feedbackStatus').textContent = response.ok
        ? 'Thank you - feedback saved.'
        : 'Feedback could not be saved.';

      if (response.ok) {
        refreshSummary();
      }

    } catch (error) {
      console.error('Feedback error:', error);

      $('feedbackStatus').textContent =
        'Connection problem. Feedback could not be saved.';
    }
  };
});

// Dashboard summary
async function refreshSummary() {
  try {
    const response = await fetch('/interactions/summary');

    if (!response.ok) {
      throw new Error('Dashboard request failed.');
    }

    const data = await response.json();

    $('total').textContent = data.total_interactions;

    $('eligible').textContent =
      `${data.documented_natlas_voice_interactions} / ${data.validation_target}`;

    $('helpful').textContent =
      data.average_helpfulness ?? '—';

  } catch (error) {
    console.error('Dashboard refresh error:', error);
  }
}

// Initial dashboard load
refreshSummary();
