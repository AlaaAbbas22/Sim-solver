import * as THREE from 'three';
import React, { useLayoutEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import axios from 'axios';
axios.defaults.withCredentials = true;

// Line Component using Three.js
function Line({ start, end, color }) {
  const ref = useRef();
  useLayoutEffect(() => {
    ref.current.geometry.setFromPoints([start, end].map((point) => new THREE.Vector3(...point)));
  }, [start, end]);
  return (
    <line ref={ref}>
      <bufferGeometry />
      <lineBasicMaterial color={color} />
    </line>
  );
}

// Game Component
function Six() {
  const [player, setPlayer] = useState([]);
  const [AI, setAI] = useState([]);
  const [choices, setChoices] = useState([]);
  const [choice, setChoice] = useState(null);
  const [screen, setScreen] = useState('not started');
  const [loser, setLoser] = useState('None');
  const [difficulty, setDifficulty] = useState(1)

  // Starting the gaem
  async function start() {
    setScreen('loading');
    const data = await axios.post('http://localhost:4000/start', {difficulty});
    const cs = data.data.available.sort();  
    setChoices(cs);
    setScreen('started');
  }

  // sending the user's choice to the backend
  async function play() {
    if (choice == null) {
      return;
    }
    setScreen('loading');
    setPlayer((old) => [...old, choice]);
    const data = await axios.post('http://localhost:4000/respond', { response: choice });
    if (data.data.lost) {
      setScreen('ended');
      setLoser(data.data.lost);
      if (data.data.lost === 'AI') {
        setAI((old) => [...old, data.data.move]);
      }
    } else {
      setScreen('started');
      const cs = data.data.available.sort();
      console.log(cs)
      setChoices(cs);
      setAI((old) => [...old, data.data.move]);
    }
  }

  // locations of the points
  const points = [
    [-7, -1.5, 0],
    [-3.5, 1, 0],
    [1, 1, 0],
    [4, -1.5, 0],
    [1, -3.5  , 0],
    [-3.5, -3.5, 0]
  ];

  // locations of the numbers
  const numbers = [
    [7, 1.5, 0],
    [4, -1.65, 0],
    [-1, -1.65 , 0],
    [-4, 1.5, 0],
    [-1, 3.3, 0],
    [4, 3.3, 0],
  ];

  return (
    <div className="min-h-screen bg-gradient-to-r from-gray-900 to-gray-800 text-white">
      <div className="container mx-auto py-10 px-4">
        <h1 className="text-4xl font-bold text-center mb-8">SIM Game</h1>
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="w-full md:w-1/2">
            {screen === 'not started' && (
              <div className="flex flex-col items-center gap-4">
                <label>Select the difficulty of the game (1 is the easiest)</label>
                <select value={difficulty} onChange={(e)=>setDifficulty(e.target.value)}>
                  {[1,2,3,4,5,6,7,8].map((item)=>
                  <option value={item}>{item}</option>)}
                </select>
                <button
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-semibold"
                  onClick={start}
                >
                  Start Game
                </button>
              </div>
            )}

            {screen === 'loading' && (
              <div className="text-center text-lg font-semibold">Loading...</div>
            )}

            {screen === 'started' && (
              <div className="flex flex-col items-center gap-4">
                <label className="text-lg font-medium">Select Your Move</label>
                <select
                  value={choice}
                  onChange={(e) => setChoice(e.target.value)}
                  className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none"
                >
                  <option value={null}>None</option>
                  {choices.map((item) => (
                    <option key={item} value={item}>
                      {item.toString()}
                    </option>
                  ))}
                </select>
                <button
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg text-lg font-semibold"
                  onClick={play}
                >
                  Submit
                </button>
              </div>
            )}

            {screen === 'ended' && (
              <div className="flex flex-col items-center gap-4">
                <h2 className="text-2xl font-semibold">
                  Winner: {loser === 'player' ? 'AI' : 'You'}
                </h2>
                <button
                  className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg text-lg font-semibold"
                  onClick={() => window.location.reload()}
                >
                  Restart Game
                </button>
              </div>
            )}
          </div>

          <div className="w-full md:w-1/2 h-[400px]">
            <Canvas>
              <ambientLight intensity={0.5} />
              <spotLight position={[10, 10, 10]} angle={0} penumbra={10} />
              <pointLight position={[-10, -10, -10]} />
              {points.map((index, i) =>
                points.map((jindex, j) =>
                  i < j &&
                  (player.some((e) => e.toString() === [i, j].toString()) ||
                    AI.some((e) => e.toString() === [i, j].toString())) && (
                    <Line
                      key={`${i}-${j}`}
                      start={points[i]}
                      end={points[j]}
                      color={
                        player.some((e) => e.toString() === [i, j].toString())
                          ? 'blue'
                          : AI.some((e) => e.toString() === [i, j].toString())
                          ? 'red'
                          : 'transparent'
                      }
                    />
                  )
                )
              )}
              {numbers.map((item, index) => (
                <Text
                  key={index}
                  scale={[1, 1, 1]}
                  color="white"
                  anchorX={numbers[index][0]}
                  anchorY={numbers[index][1]}
                  textAlign={"right"}
                  fontSize={0.5}
                >
                  {index}
                </Text>
              ))}
            </Canvas>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Six;
