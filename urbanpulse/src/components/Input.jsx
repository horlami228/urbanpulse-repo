import React, { useState } from 'react';

function MapInput({ onSubmitLocation }) {
  const [location, setLocation] = useState('');

  const handleInputChange = (e) => {
    setLocation(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitLocation(location);
    setLocation('');  // Clear the input field after submission
  };

  return (
    <div className="flex justify-center items-center h-screen px-4 sm:px-6 lg:px-8">
      <form onSubmit={handleSubmit} className="w-full max-w-lg flex flex-col items-center">
        <input
          type="text"
          value={location}
          onChange={handleInputChange}
          className="text-base sm:text-lg p-2 sm:p-4 border border-gray-300 rounded w-full"
          placeholder="Enter location"
        />
        <button type="submit" className="mt-4 p-2 bg-blue-500 text-white rounded w-auto px-4">
          Generate Map
        </button>
      </form>
    </div>
  );
}

export default MapInput;
