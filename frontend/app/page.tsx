'use client'
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import axios from "axios";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("");
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  const startPolling = () => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get('http://localhost:5000/status');
        const { status, transcribedText, outputAudio } = response.data;
        setStatus(status);

        if (status === "Finished" || status.startsWith("Error")) {
          clearInterval(interval);
          setLoading(false);
          setProcessing(false);
          if (transcribedText) setMessage(transcribedText);
        } else if (status === "Recording stopped by user") {
          clearInterval(interval);
          setLoading(false);
          setMessage("Recording stopped by user.");
        } else if (status === "Transcribing..." || status === "Converting to speech...") {
          setProcessing(true);
        }
      } catch (error) {
        console.error("Error fetching status:", error);
        clearInterval(interval);
        setLoading(false);
        setProcessing(false);
      }
    }, 500);
    setPollingInterval(interval);
  };

  const handleClick = async (endpoint: string) => {
    setLoading(true);
    setProcessing(false);
    setStatus("Starting recording...");
    setMessage("");

    try {
      await axios.post(`http://localhost:5000/${endpoint}`);
      startPolling();
    } catch (error) {
      setMessage("Error starting recording.");
      setLoading(false);
    }
  };

  const handleStop = async () => {
    if (pollingInterval) clearInterval(pollingInterval);
    try {
      await axios.post('http://localhost:5000/stop');
      setStatus("Stopping...");
      setLoading(false);
      setProcessing(false);
    } catch (error) {
      setMessage("Error stopping recording.");
    }
  };

  useEffect(() => {
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, [pollingInterval]);

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <div className="flex items-center gap-4">
          <Button onClick={() => handleClick("indiatous")} disabled={loading || processing}>
            {loading ? <Loader2 className="animate-spin" /> : "India To US"}
          </Button>
          <Button onClick={handleStop} disabled={!loading && !processing}>
            Stop
          </Button>
        </div>
        {(status || message) && (
          <Card className="w-full max-w-md">
            <CardContent className="p-4 text-center">
              {status && <p className="text-blue-500 font-medium">{status}</p>}
              {message && <p>{message}</p>}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}