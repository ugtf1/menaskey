// static/js/app.js
(function() {
  // CSRF helper
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  // Quote form logic
  const form = document.getElementById('quoteForm');
  const statusEl = document.getElementById('formStatus');

  function setStatus(text, ok=false) {
    statusEl.textContent = text;
    statusEl.classList.remove('ok','err');
    statusEl.classList.add(ok ? 'ok' : 'err');
  }

  function clearErrors() {
    form.querySelectorAll('.error').forEach(e => e.textContent = '');
  }

  function inlineValidate() {
    let valid = true;
    clearErrors();
    const fields = ['name','phone','service'];
    fields.forEach(name => {
      const input = form.querySelector(`[name="${name}"]`);
      if (!input.value.trim()) {
        input.nextElementSibling.textContent = 'Required';
        valid = false;
      } else if (name === 'phone') {
        const re = /^[0-9+\-\s()]{7,}$/;
        if (!re.test(input.value.trim())) {
          input.nextElementSibling.textContent = 'Enter a valid phone';
          valid = false;
        }
      }
    });
    const email = form.querySelector('[name="email"]');
    if (email.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value)) {
      email.nextElementSibling.textContent = 'Enter a valid email';
      valid = false;
    }
    return valid;
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!inlineValidate()) {
        setStatus('Please fix errors above.');
        return;
      }

      const btn = form.querySelector('.btn.submit');
      btn.disabled = true;
      btn.classList.add('loading');
      setStatus('Submitting…');

      const payload = {
        name: form.name.value.trim(),
        phone: form.phone.value.trim(),
        email: form.email.value.trim(),
        service: form.service.value.trim(),
        message: form.message.value.trim(),
        company: form.company.value.trim() // honeypot
      };

      try {
        const res = await fetch('/api/quote', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.status === 'ok') {
          setStatus(data.message || 'Submitted. We’ll reach out shortly.', true);
          form.reset();
        } else if (data.status === 'ignored') {
          // honeypot triggered; show generic success
          setStatus('Thanks! We’ll reach out shortly.', true);
          form.reset();
        } else {
          // display field errors if any
          if (data.errors) {
            Object.entries(data.errors).forEach(([field, msgs]) => {
              const input = form.querySelector(`[name="${field}"]`);
              if (input) input.nextElementSibling.textContent = msgs.join(', ');
            });
          }
          setStatus('Please review and try again.');
        }
      } catch (err) {
        setStatus('Network error. Please try again.');
      } finally {
        btn.disabled = false;
        btn.classList.remove('loading');
      }
    });
  }

  // StickyCallBar: GTM + server click logging + CallRail compatible behavior
  const bar = document.getElementById('stickyCallBar');
  const link = document.getElementById('stickyCallLink');

  function pushGTM(phone) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: 'phone_click',
      phone: phone,
      component: 'sticky_call_bar',
      timestamp: new Date().toISOString()
    });
  }

  async function logClick(event_type) {
    try {
      await fetch('/api/click', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ event_type })
      });
    } catch(e) {}
  }

  if (link) {
    link.addEventListener('click', () => {
      const phone = bar?.dataset.phone || '';
      pushGTM(phone);
      logClick('call');
      // CallRail: if you use dynamic number insertion (DNI), ensure tel: matches displayed number or let CallRail DNI handle tracking at the number level.
    });
  }

  // Track important website click (example: hero CTA)
  document.querySelectorAll('a,button').forEach(el => {
    if (el.classList.contains('primary') || el.classList.contains('nav-link')) {
      el.addEventListener('click', () => logClick('website'));
    }
  });
})();