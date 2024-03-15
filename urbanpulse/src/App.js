import React, { useState, useEffect } from 'react';
import Header from './components/Header.jsx'
import MapInput from './components/Input.jsx'
import FoliumMap from './components/foliumMap.jsx'

function App() {
  const [mapUrl, setMapUrl] = useState('');

  useEffect(() => {
    // Generate an initial map with no specific location
    const initialMapUrl = `http://localhost:5000/map?location=None`;
    setMapUrl(initialMapUrl);
  }, []);

  const handleLocationSubmit = (location) => {
    const url = location
      ? `http://localhost:5000/map?location=${encodeURIComponent(location)}`
      : `http://localhost:5000/map?location=None`;
    setMapUrl(url);
  };

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <FoliumMap mapUrl={mapUrl} />
      <MapInput onSubmitLocation={handleLocationSubmit} />
    </div>
  );
}

export default App;
