import "react";
import { useState, useEffect } from "react";
import { MCQChallenge } from "./MCQChallenge";
import { useApi } from "../utils/api";
import { useAuth } from "@clerk/clerk-react";

export function ChallengeGenerator() {
  const [challenge, setChallenge] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [difficulty, setDifficulty] = useState("easy");
  const [quota, setQuota] = useState(null);
  const {makeRequest}=useApi()

  const {isLoaded,isSignedIn}=useAuth();

  useEffect(()=>{
    if(isLoaded && isSignedIn){
    fetchQuota()
    }
  },[isLoaded,isSignedIn])

  const fetchQuota = async () => {
    try{
      const data=await makeRequest("quota")
      setQuota(data)

    }catch(err){
      console.log(err)
    }
  };

  const generateChalenge = async () => {
    setIsLoading(true)
    setError(null)
    try{
      const data=await makeRequest("generate-challenge",{
        method:"POST",
        body:JSON.stringify({difficulty})
      })
      setChallenge(data)
      console.log(data)
      fetchQuota()
    }catch(err){
      setError(err.message|| "Failed to generate Challenge")
      console.log(err)
    }finally{
      setIsLoading(false)
    }
  };

  const getNextResetTime = () => {
    if (!quota?.last_reset_data) return null;
    const resetDate=new Date(quota.last_reset_data)
    resetDate.setHours(resetDate.getHours()+24)
    return resetDate
  };

  return (
    <div className="challenge-container">
      <h2>Coding Chalenge Generator</h2>
      <div className="quota-display">
        <p>Challenges Remaining today: {quota?.quota_remaining || 0}</p>
        {quota?.quota_remaining === 0 && <p>Next reset: {getNextResetTime()?.toLocaleString()}</p>}
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
      <button onClick={generateChalenge} disabled={isLoading|| quota?.quota_remaining ===0} className="generate-button">{isLoading? "Generating...":"Generate Chalenge"}</button>
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
