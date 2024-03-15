function FoliumMap({ mapUrl }) {
    return (
      <div className="w-full h-screen">
        <iframe
          src={mapUrl}
          className="w-full h-full"
          style={{ height: '60vh' }} // Adjust height based on your needs
          frameBorder="0"
          title="Map"
        ></iframe>
      </div>
    );
  }

export default FoliumMap;
