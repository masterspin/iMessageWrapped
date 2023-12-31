import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Plotly from "plotly.js"
import createPlotlyComponent from "react-plotly.js/factory";
import dynamic from 'next/dynamic';
import { css } from '@emotion/react';
import { SyncLoader } from 'react-spinners';

const override = css`
  display: block;
  margin: 0 auto;
  border-color: red;
`;

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

const Loading: React.FC = () => {
  const router = useRouter();
  const [loadingTextIndex, setLoadingTextIndex] = useState(0);
  const medals = ['🥇', '🥈', '🥉'];
  const [randomColors, setRandomColors] = useState<string[]>([]);
  const [responseData, setResponseData] = useState<any>({}); // State to hold response data
  const [dataLoaded, setDataLoaded] = useState(false); // State to track data loading
  const loadingTexts = ['Wrapping up your texts','Copying Contact Information and Message History', 'Assigning names to phone numbers', 'Reading Messages', 'Creating Graphs', 'Grabbing Game Pigeon Data','Grabbing data about your most commonly used words','Removing common phrases and words from the list','Grabbing data about how many texts you\'ve sent and received with each friend','Grabbing data about which group chats where you were most active in','Grabbing data about your most active group chats','Grabbing data about the person who you\'ve received the most texts from','Grabbing data about the person who you\'ve sent the most texts to', 'Grabbing most used emojis', 'Graphing average response time between users']; // Add more texts as needed
  useEffect(() => {
    const interval = setInterval(() => {
      setLoadingTextIndex((prevIndex) => (prevIndex + 1) % loadingTexts.length);
    }, 10000); // Change text every 5 seconds (adjust speed as needed)

    const analyze = async () => {
      try {
        const response = await fetch('https://i-message-wrapped-iy127bmv4-masterspin.vercel.app/analyze');
        if (response.status >= 200 && response.status < 300) {
          console.log('API call successful');
          clearInterval(interval);
          const data = await response.json();
          // For example, if your response contains a plot HTML
          // and you want to render it in a div with ID "plotContainer"
          setResponseData(data)
          setDataLoaded(true); // Set dataLoaded to true after receiving data
        } else {
          console.error('API call failed');
          router.push('/error');
        }
      } catch (error) {
        console.error('Error occurred:', error);
      }
    };

    analyze();

    return () => clearInterval(interval); // Clean up the interval on unmount
  }, [loadingTexts.length, router]);// Add router to the dependencies to prevent stale references

  function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }
  
  // Generate random colors for each bar
  useEffect(() => {
    if (responseData.gamePigeonData) {
      const colors = Object.values(responseData.gamePigeonData).map(() => getRandomColor());
      setRandomColors(colors);
    }
    if (responseData.numbersSent) {
      const colors = Object.values(responseData.numbersSent).map(() => getRandomColor());
      setRandomColors(colors);
    }
  }, [responseData]);


  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-200">
      {!dataLoaded ? (
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4" style={{color:"#008bff"}}>{loadingTexts[loadingTextIndex]} <span><SyncLoader color={'#008bff'} loading={true} size={10} /></span></h1>
          <p className="text-gray-800">Please wait while we process your request.</p>
          <p className="text-gray-400">This may take a few minutes.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
          {/* Card for displaying total messages */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">Total Messages</h2>
            <p>{responseData.total_messages}</p>
          </div>
  
          {/* Card for displaying total sent */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">Total Sent</h2>
            <p>{responseData.total_sent}</p>
          </div>
  
          {/* Card for displaying total received */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">Total Received</h2>
            <p>{responseData.total_received}</p>
          </div>
  
          {/* Card for displaying top 3 sent direct messages */}
          {dataLoaded && responseData.top_3_receivedDM_with_freq && (
            <div className="col-span-3 md:col-span-2 lg:col-span-3 bg-white rounded-lg shadow-md p-4">
              <h2 className="text-xl font-semibold mb-2">Top People You&apos;ve Sent Direct Messages To</h2>
              <ul>
                {Array.isArray(responseData.top_3_receivedDM_with_freq) &&
                  responseData.top_3_receivedDM_with_freq.map((data:any, index:number) => (
                    <li key={index}>
                      {medals[index]}: Received {data.frequency} messages from {data.name}
                    </li>
                  ))}
              </ul>
            </div>
          )}

          {dataLoaded && responseData.top_3_receivedDM_with_freq && (
            <div className="col-span-3 md:col-span-2 lg:col-span-3 bg-white rounded-lg shadow-md p-4">
              <h2 className="text-xl font-semibold mb-2">Top People You&apos;ve Received Direct Messages From</h2>
              <ul>
                {Array.isArray(responseData.top_3_receivedDM_with_freq) &&
                  responseData.top_3_receivedDM_with_freq.map((data:any, index:number) => (
                    <li key={index}>
                      {medals[index]}: Received {data.frequency} messages from {data.name}
                    </li>
                  ))}
              </ul>
            </div>
          )}

          {dataLoaded && responseData.common_words && (
            <div className="bg-white rounded-lg shadow-md p-4">
                <h2 className="text-xl font-semibold mb-2">Most Used Words</h2>
                <ul>
                {responseData.common_words.map((wordData:any, index:number) => (
                    <li key={index}>
                    {wordData.word} - {wordData.count} times
                    </li>
                ))}
                </ul>
            </div>
            )}
  
          {/* Card for displaying top 3 received direct messages */}
          {dataLoaded && responseData.top_3_groupChats_with_freq && (
            <div className="col-span-2 bg-white rounded-lg shadow-md p-4">
              <h2 className="text-xl font-semibold mb-2">Most Active Group Chats</h2>
              <ul>
                {Array.isArray(responseData.top_3_groupChats_with_freq) &&
                  responseData.top_3_groupChats_with_freq.map((data:any, index:number) => (
                    <li key={index}>
                      {medals[index]}: {data.name}
                    </li>
                  ))}
              </ul>
            </div>
          )}

          {dataLoaded && responseData.common_emojis && (
            <div className="bg-white rounded-lg shadow-md p-4">
                <h2 className="text-xl font-semibold mb-2">Most Used Emojis</h2>
                <ul>
                {responseData.common_emojis.map((emojiData:any, index:number) => (
                    <li key={index}>
                    {emojiData.emoji} - {emojiData.count} times
                    </li>
                ))}
                </ul>
            </div>
            )}

          {dataLoaded && responseData.top_3_groupChats_sent_with_freq && (
            <div className="col-span-2 bg-white rounded-lg shadow-md p-4">
              <h2 className="text-xl font-semibold mb-2">Group Chats You Were Most Active In</h2>
              <ul>
                {Array.isArray(responseData.top_3_groupChats_sent_with_freq) &&
                  responseData.top_3_groupChats_sent_with_freq.map((data:any, index:number) => (
                    <li key={index}>
                      {medals[index]}: {data.name}
                    </li>
                  ))}
              </ul>
            </div>
          )}
  
          {/* Plot Card */}
          {dataLoaded && responseData.numbersSent && (
          <div className="col-span-3 md:col-span-2 lg:col-span-3 bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">Messages Sent (Group Chats Included)</h2>
            <div className="plot-container">
              <Plot
                data={[
                  {
                    x: Object.keys(responseData.numbersSent),
                    y: Object.values(responseData.numbersSent),
                    type: 'bar',
                    marker: {
                      color: randomColors,
                    },
                  },
                ]}
                layout={{
                  width: 800,
                  height: 400,
                  yaxis: {
                    automargin: true,
                  },
                  xaxis: {
                    automargin: true,
                  },
                }}
              />
            </div>
          </div>
        )}
        {dataLoaded && responseData.numbersReceived && (
          <div className="col-span-3 md:col-span-2 lg:col-span-3 bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">Messages Received (Group Chats Included)</h2>
            <div className="plot-container">
              <Plot
                data={[
                  {
                    x: Object.keys(responseData.numbersReceived),
                    y: Object.values(responseData.numbersReceived),
                    type: 'bar',
                    marker: {
                      color: randomColors,
                    },
                  },
                ]}
                layout={{
                  width: 800,
                  height: 400,
                  yaxis: {
                    automargin: true,
                  },
                  xaxis: {
                    automargin: true,
                  },
                }}
              />
            </div>
          </div>
        )}
        {dataLoaded && responseData.averageResponse && (
          <div className="col-span-3 md:col-span-2 lg:col-span-3 bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">Average Direct Message Response Time</h2>
            <div className="plot-container">
              <Plot
                data={[
                  {
                    x: Object.keys(responseData.averageResponse),
                    y: Object.values(responseData.averageResponse),
                    type:'linear',
                    marker: {
                      color: randomColors,
                    },
                  },
                ]}
                layout={{
                  width: 800,
                  height: 400,
                  yaxis: {
                    automargin: true,
                    title: "Minutes",
                  },
                  xaxis: {
                    automargin: true,
                  },
                }}
              />
            </div>
          </div>
        )}
         {dataLoaded && responseData.gamePigeonData && (
          <div className="col-span-3 md:col-span-2 lg:col-span-3 bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">Game Pigeon Usage</h2>
            <div className="plot-container">
              <Plot
                data={[
                  {
                    y: Object.keys(responseData.gamePigeonData),
                    x: Object.values(responseData.gamePigeonData),
                    type: 'bar',
                    orientation: 'h',
                    marker: {
                      color: randomColors,
                    },
                  },
                ]}
                layout={{
                  width: 800,
                  height: 400,
                  yaxis: {
                    automargin: true,
                  },
                  xaxis: { title: 'Rounds Played' },
                }}
              />
            </div>
          </div>
        )}
        </div>
      )}
    </div>
  );
  
};

export default Loading;
