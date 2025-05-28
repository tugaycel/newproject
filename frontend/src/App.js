import React, { useState } from 'react';

function App() {
  const [outfit, setOutfit] = useState('');
  const [files, setFiles] = useState([]);

  const upload = async () => {
    const formData = new FormData();
    for (let file of files) {
      formData.append('files', file);
    }

    const res = await fetch(process.env.REACT_APP_BACKEND_URL + "/suggest", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setOutfit(data.outfits);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Closet Stylist AI</h2>
      <input type="file" multiple onChange={e => setFiles(e.target.files)} />
      <button onClick={upload}>Get Outfit Ideas</button>
      <pre style={{ marginTop: 20, whiteSpace: 'pre-wrap' }}>{outfit}</pre>
    </div>
  );
}

export default App;