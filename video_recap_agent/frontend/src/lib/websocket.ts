import Cookies from "js-cookie";
import type { ProgressEvent } from "./types";

function getWsUrl(): string {
  if (process.env.NEXT_PUBLIC_WS_URL) return process.env.NEXT_PUBLIC_WS_URL;
  if (typeof window === "undefined") return "ws://localhost:8000";
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}`;
}

const WS_URL = getWsUrl();

export class JobWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private jobId: string;
  private onMessage: (data: ProgressEvent) => void;
  private onClose?: () => void;

  constructor(
    jobId: string,
    onMessage: (data: ProgressEvent) => void,
    onClose?: () => void
  ) {
    this.jobId = jobId;
    this.onMessage = onMessage;
    this.onClose = onClose;
  }

  connect() {
    const token = Cookies.get("access_token");
    if (!token) return;

    this.ws = new WebSocket(
      `${WS_URL}/api/v1/ws/jobs/${this.jobId}?token=${token}`
    );

    this.ws.onmessage = (event) => {
      const data: ProgressEvent = JSON.parse(event.data);
      this.onMessage(data);
      if (data.type === "completed" || data.type === "failed") {
        this.disconnect();
      }
    };

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = Math.pow(2, this.reconnectAttempts) * 1000;
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, delay);
      } else {
        this.onClose?.();
      }
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect() {
    this.reconnectAttempts = this.maxReconnectAttempts;
    this.ws?.close();
    this.ws = null;
  }
}
