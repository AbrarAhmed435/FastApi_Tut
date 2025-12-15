import React from "react";
import { useState, useEffect } from "react";
import { MCQChallenge } from "../challenge/MCQChallenge";
import { useApi } from "../utils/api";


export function HistoryPanel() {
  const {makeRequest}=useApi()
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null)
    try{
      const res=await makeRequest('my-history')
      console.log(res)
      setHistory(res.challenges || [])
    }catch(err){
      setError("Failed to load history")
    }finally{
      setIsLoading(false)
    }
  };

  if (isLoading) {
    return <div className="loading">Loading History...</div>;
  }

  if (error) {
    return (
      <div className="error=message">
        <p>{error}</p>
        <button onClick={fetchHistory}>Retry</button>
      </div>
    );
  }

  return (
    <div className="history-panel">
      <h2>History</h2>
      {history.length === 0 ? (
        <p>No challenge history</p>
      ) : (
        <div className="history-list">
          {history.map((challenge) => {
            return (
              <MCQChallenge
                challenge={challenge}
                key={challenge.id}
                showExplanation
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
