import { Track } from "./data/types";
import { hashString } from "./utils/colors";

class AudioPreviewEngine {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private intervalId: any = null;
  private isRunning: boolean = false;
  private step: number = 0;
  private volume: number = 0.8;
  private currentTrack: Track | null = null;

  private initContext() {
    if (typeof window === "undefined") return;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      this.ctx = new AudioCtx();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(this.volume, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);
    }
    if (this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  }

  public setVolume(vol: number) {
    this.volume = Math.max(0, Math.min(1, vol));
    if (this.masterGain && this.ctx) {
      this.masterGain.gain.setTargetAtTime(this.volume, this.ctx.currentTime, 0.05);
    }
  }

  public play(track: Track) {
    this.initContext();
    if (!this.ctx || !this.masterGain) return;

    this.stop();
    this.currentTrack = track;
    this.isRunning = true;
    this.step = 0;

    // Base frequencies derived deterministically from track properties
    const seed = hashString(track.id + track.title);
    const rootFreq = 130.81 * Math.pow(2, (seed % 12) / 12); // C3 octave range
    const isMinor = (track.audio_features?.mode ?? 1) === 0;

    // Chord ratios: Major vs Minor triad
    const ratios = isMinor ? [1, 1.2, 1.5, 1.8] : [1, 1.25, 1.5, 1.875];
    const bpm = track.audio_features?.tempo || (90 + (seed % 60));
    const stepDuration = 60 / bpm / 2; // eighth notes

    const playNote = (freq: number, duration: number, type: OscillatorType = "sine", gainVal = 0.15) => {
      if (!this.ctx || !this.masterGain || !this.isRunning) return;
      try {
        const osc = this.ctx.createOscillator();
        const noteGain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

        noteGain.gain.setValueAtTime(0, this.ctx.currentTime);
        noteGain.gain.linearRampToValueAtTime(gainVal, this.ctx.currentTime + 0.02);
        noteGain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);

        osc.connect(noteGain);
        noteGain.connect(this.masterGain);

        osc.start();
        osc.stop(this.ctx.currentTime + duration);
      } catch {
        // Ignore audio playback context errors
      }
    };

    // Play initial warm pad chord
    ratios.forEach((r, idx) => {
      playNote(rootFreq * r, 2.5, "triangle", 0.08);
      if (idx === 0) playNote(rootFreq * 0.5, 3.0, "sine", 0.12); // Bass
    });

    // Schedule harmonic rhythm loop
    this.intervalId = setInterval(() => {
      if (!this.isRunning || !this.ctx) return;
      const beat = this.step % 8;
      const ratio = ratios[this.step % ratios.length];
      const octave = (this.step % 4 === 0) ? 2 : 1;

      // Play melodic synth arpeggio
      playNote(rootFreq * ratio * octave, stepDuration * 0.9, "sine", 0.12);

      // Bass note on downbeats
      if (beat === 0 || beat === 4) {
        playNote(rootFreq * 0.5, stepDuration * 1.8, "triangle", 0.18);
      }

      this.step++;
    }, stepDuration * 1000);
  }

  public stop() {
    this.isRunning = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.step = 0;
  }
}

export const audioSynth = new AudioPreviewEngine();
