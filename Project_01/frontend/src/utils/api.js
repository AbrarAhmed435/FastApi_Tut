import React from "react";
import {useAuth} from '@clerk/clerk-react'

export const useApi=()=>{
    const {getToken}=useAuth();
    const makeRequest= async (endpoint,options={})=>{
        const token= await getToken()
        // console.log("Token=",token)
        const defaultOptions={
            headers:{
                "Content-Type":"application/json",
                "Authorization":`Bearer ${token}`
            }
        }
        
        const response=await fetch(`http://localhost:8000/api/${endpoint}`,{
            ...defaultOptions,
            ...options,
            // headers:{
            //     ...defaultOptions.headers,
            //     ...options.headers,
            // },
        })
        
        if (!response.ok){
            console.log(response)
            const errorData=await response.json().catch(()=>null)
            if (response.status==429){
                throw new Error("Daily quota exceeded")
            }
            throw new Error(errorData?.detail || "An error occured")
            
        }

        return response.json()
    }
    return {makeRequest}
}
