'use client'
import React, {useEffect} from 'react'

const Page = async () => {
    const [festivals, setFestivals] = useState()





    return (
        <>
            <div>Circus Agent Frontend</div>
            {festivals.length > 0 ? (
                <ul>
                    {festivals.map((f) => (
                        <li key={f.id}>{f.name}</li>
                    ))}
                </ul>
            ) : (<p>No festivals found!</p>)
            }
        </>
    )
}

export default Page
