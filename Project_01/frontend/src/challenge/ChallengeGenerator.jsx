import "react";
import { useState, useEffect } from "react";
import { MCQChallenge } from "./MCQChallenge";

export function ChallengeGenerator() {
  const [challenge, useChallenge] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [difficulty, setDifficulty] = useState("easy");
  const [quota, setQuota] = useState(null);

  const fetchQuota = async () => {};

  const generateChalenge = async () => {};

  const getNextResetTime = () => {};

  return (
    <div className="challenge-container">
      <h2>Coding Chalenge Generator</h2>
      <div className="quota-display">
        <p>Challenges Remaining today: {quota?.quota_remaining || 0}</p>
        {quota?.quota_remaining === 0 && <p>Next reset: {0}</p>}
      </div>
      <div className="difficulty-selector">
        <label htmlFor="difficulty">Select difficulty</label>
        <select
          id="difficulty"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          disabled={isLoading}
        >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
        </select>
      </div>
      <button onClick={generateChalenge} disabled={isLoading|| quota?.quota.quota_remaining ===0} className="generate-button">{isLoading? "Generating...":"Generate Chalenge"}</button>
      {error && (
        <div className="error-message">
            <p>{error}</p>
        </div>
      )}
      {challenge && (
        <MCQChallenge challenge={challenge}/>
      )}
    </div>
  );
}
