
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
let voiceRequestPending = false;

async function waitForVoiceJob(jobId) {
  if (sessionStorage.getItem('vbVoiceJobTimedOut') === jobId) {
    $('status').textContent =
      'Your previous request exceeded the waiting period. ' +
      'Please contact the test coordinator before recording again.';
    return;
  }

  for (let attempt = 0; attempt < 150; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 3000));

    try {
      const response = await fetch(
        '/voice/status/' + encodeURIComponent(jobId),
        { cache: 'no-store' }
      );

      if (!response.ok) {
        if (response.status === 404) {
          sessionStorage.removeItem('vbPendingVoiceJob');
          sessionStorage.removeItem('vbVoiceJobTimedOut');
          $('status').textContent =
            'Your previous voice request is no longer available. ' +
            'Please record your question again.';
          return;
        }
        continue;
      }

      const data = await response.json();

      if (data.status === 'completed') {
        sessionStorage.removeItem('vbPendingVoiceJob');
          sessionStorage.removeItem('vbVoiceJobTimedOut');
        render(data.result);
        return;
      }

      if (data.status === 'failed') {
        sessionStorage.removeItem('vbPendingVoiceJob');
          sessionStorage.removeItem('vbVoiceJobTimedOut');
        $('status').textContent =
          data.error || 'Voice processing failed.';
        return;
      }

      $('status').textContent =
        'N-ATLAS is processing your question. Please wait...';

    } catch (error) {
      console.warn('Voice polling issue:', error);
      $('status').textContent =
        'Reconnecting to your voice request. Please wait...';
    }
  }

  sessionStorage.setItem('vbVoiceJobTimedOut', jobId);

  $('status').textContent =
    'Your request is taking longer than expected. ' +
    'Please contact the test coordinator before recording again.';
}

async function sendAudio(blob) {
  if (voiceRequestPending) {
    $('status').textContent =
      'Your previous question is still being processed.';
    return;
  }

  const existingJob = sessionStorage.getItem('vbPendingVoiceJob');

  if (existingJob) {
    $('status').textContent =
      'Recovering your previous voice request...';
    voiceRequestPending = true;
    try {
      await waitForVoiceJob(existingJob);
    } finally {
      voiceRequestPending = false;
    }
    return;
  }

  voiceRequestPending = true;
  $('status').textContent = 'Submitting your voice question...';

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
    const response = await fetch('/voice/submit', {
      method: 'POST',
      body: form
    });

    const data = await response.json();

    if (!response.ok) {
      $('status').textContent =
        typeof data.detail === 'string'
          ? data.detail
          : 'Voice submission failed.';
      return;
    }

    if (!data.job_id) {
      throw new Error('The server did not return a job ID.');
    }

    sessionStorage.setItem('vbPendingVoiceJob', data.job_id);

    $('status').textContent =
      'Recording received. N-ATLAS is preparing your answer...';

    await waitForVoiceJob(data.job_id);

  } catch (error) {
    console.error('Voice request error:', error);

    $('status').textContent =
      'Connection interrupted. Please contact the test ' +
      'coordinator before submitting another recording.';
  } finally {
    voiceRequestPending = false;
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


async function recoverPendingVoiceJob() {
  const jobId = sessionStorage.getItem('vbPendingVoiceJob');

  if (!jobId || voiceRequestPending) {
    return;
  }

  voiceRequestPending = true;
  $('status').textContent =
    'Restoring your previous voice request. Please wait...';

  try {
    await waitForVoiceJob(jobId);
  } finally {
    voiceRequestPending = false;
  }
}

recoverPendingVoiceJob();
