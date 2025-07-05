import {useEffect} from "react";

useEffect(()=>{
        const fetchFestivals = async () =>{
            const data = await fetch('http://localhost:8000/api/festivals')
            const festivals = await data.json()

            setFestivals(festivals);
        }
        fetchFestivals()
    }, [],

    )