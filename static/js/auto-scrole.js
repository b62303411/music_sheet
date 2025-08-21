 // --- Demo filler (remove in your page) ---


    (function autoScroll(){
      'use strict';

      // TARGET: scroll the whole page (window). To scroll a container instead, set:
      // const target = document.getElementById('content'); and flip USE_WINDOW to false.
      const USE_WINDOW = true;
      const target = USE_WINDOW ? window : document.getElementById('song-content');

      // UI
      const playPauseBtn = document.getElementById('playPause');
      const speedRange   = document.getElementById('speedRange');
      const speedNum     = document.getElementById('speedNum');
      const mmssInput    = document.getElementById('mmss');
      const applyDurBtn  = document.getElementById('applyDur');
      const loopChk      = document.getElementById('loopChk');
      const toTopBtn     = document.getElementById('toTop');

      // State
      let speed = Number(speedRange.value); // px per second
      let running = false;
      let rafId = null;
      let lastTs = null;

      const getMaxScroll = () => {
        if (USE_WINDOW) {
          const doc = document.scrollingElement || document.documentElement;
          return doc.scrollHeight - window.innerHeight;
        } else {
          return target.scrollHeight - target.clientHeight;
        }
      };
      const getPos = () => USE_WINDOW ? (window.scrollY || window.pageYOffset) : target.scrollTop;
      const setPos = (y) => {
        if (USE_WINDOW) window.scrollTo({ top: y, behavior: 'auto' });
        else target.scrollTop = y;
      };
      const by = (dy) => {
        if (USE_WINDOW) window.scrollBy(0, dy);
        else target.scrollTop += dy;
      };

      function step(ts){
        if (!running) return;
        if (lastTs == null) lastTs = ts;
        const dt = (ts - lastTs) / 1000; // seconds
        lastTs = ts;
        const dy = speed * dt;

        by(dy);

        const pos = getPos();
        const max = getMaxScroll();
        if (pos >= max - 1) {
          if (loopChk.checked) {
            setPos(0);
          } else {
            pause();
            return;
          }
        }
        rafId = requestAnimationFrame(step);
      }

      function play(){
        if (running || speed <= 0) return;
        running = true;
        playPauseBtn.textContent = '⏸ Pause';
        playPauseBtn.setAttribute('aria-pressed', 'true');
        lastTs = null;
        rafId = requestAnimationFrame(step);
      }

      function pause(){
        running = false;
        playPauseBtn.textContent = '▶ Play';
        playPauseBtn.setAttribute('aria-pressed', 'false');
        if (rafId) cancelAnimationFrame(rafId);
        rafId = null; lastTs = null;
      }

      function toggle(){ running ? pause() : play(); }

      function syncSpeedInputs(val){
        const v = Math.max(0, Number(val) || 0);
        speed = v;
        speedRange.value = String(v);
        speedNum.value = String(v);
        if (running && speed === 0) pause();
      }

      function parseMmSs(s){
        if (!s) return null;
        const m = s.trim().match(/^(\d{1,3}):([0-5]?\d)$/);
        if (!m) return null;
        const minutes = Number(m[1]);
        const seconds = Number(m[2]);
        return minutes * 60 + seconds;
      }

      function setSpeedFromDuration(sec){
        const distance = Math.max(0, getMaxScroll() - getPos());
        if (sec <= 0) return;
        const pxPerSec = Math.max(0, Math.round(distance / sec));
        syncSpeedInputs(pxPerSec);
      }

      // Wire UI
      playPauseBtn.addEventListener('click', toggle);
      speedRange.addEventListener('input', e => syncSpeedInputs(e.target.value));
      speedNum.addEventListener('input',  e => syncSpeedInputs(e.target.value));
      toTopBtn.addEventListener('click', () => setPos(0));
      applyDurBtn.addEventListener('click', () => {
        const sec = parseMmSs(mmssInput.value);
        if (sec == null) { applyDurBtn.animate([{background:'#400'},{background:'#222'}], {duration:400}); return; }
        setSpeedFromDuration(sec);
      });

      // Pause when tab hidden (saves battery), resume manually
      document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });

      // Keyboard shortcuts
      document.addEventListener('keydown', (e) => {
        if (e.target && /input|textarea|select/.test(e.target.tagName.toLowerCase())) return;
        if (e.code === 'Space') { e.preventDefault(); toggle(); }
        if (e.key === 'Home') { setPos(0); }
        if (e.key === 'ArrowUp') { e.preventDefault(); syncSpeedInputs(speed + (e.shiftKey ? 50 : 10)); }
        if (e.key === 'ArrowDown') { e.preventDefault(); syncSpeedInputs(Math.max(0, speed - (e.shiftKey ? 50 : 10))); }
      });

      // Optional: start paused at 80 px/s
      pause();

      // Expose minimal API (if you want to call from elsewhere)
      window.AutoScroll = { play, pause, setSpeed: v => syncSpeedInputs(v), setSpeedFromDuration };
    })();