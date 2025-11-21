import React, {useState} from 'react';
import axios from 'axios';

export default function App(){
  const [file, setFile] = useState(null);
  const [bg, setBg] = useState('#ffffff');
  const [copies, setCopies] = useState('6');
  const [processing, setProcessing] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [preview, setPreview] = useState(null);

  const onFileChange = (e) => {
    const f = e.target.files[0];
    if(!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if(!file) return alert('Please choose a photo');
    setProcessing(true);
    setDownloadUrl(null);
    try{
      const fd = new FormData();
      fd.append('photo', file);
      fd.append('bg_color', bg);
      fd.append('copies', copies);
      const res = await axios.post('/process', fd, { responseType: 'blob' });
      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);
    }catch(err){
      alert('Processing failed: ' + (err.message || err));
    }finally{
      setProcessing(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow p-6">
        <h1 className="text-2xl font-semibold mb-4">Passport Photo Auto — Studio</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Upload photo</label>
            <input type="file" accept="image/*" onChange={onFileChange} className="mt-1" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Background</label>
              <input value={bg} onChange={(e)=>setBg(e.target.value)} className="mt-1 p-2 border rounded w-full" />
              <div className="mt-2 flex gap-2">
                <button type="button" onClick={()=>setBg('#ffffff')} className="px-3 py-1 border rounded">White</button>
                <button type="button" onClick={()=>setBg('#3b82f6')} className="px-3 py-1 border rounded">Light Blue</button>
                <button type="button" onClick={()=>setBg('#ff0000')} className="px-3 py-1 border rounded">Red</button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Copies</label>
              <select value={copies} onChange={(e)=>setCopies(e.target.value)} className="mt-1 p-2 border rounded w-full">
                <option value="3">3</option>
                <option value="6">6</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2 items-center">
            <button disabled={processing} className="bg-blue-600 text-white px-4 py-2 rounded">
              {processing ? 'Processing...' : 'Process'}
            </button>
            {downloadUrl && <a href={downloadUrl} download="processed_photos.zip" className="px-4 py-2 border rounded">Download ZIP</a>}
          </div>
        </form>

        <div className="mt-6">
          <h3 className="text-lg font-medium">Preview</h3>
          <div className="mt-2 p-4 bg-gray-100 rounded min-h-[200px] flex items-center justify-center">
            {preview ? <img src={preview} alt="preview" className="max-h-60" /> : <div className="text-gray-500">No photo selected</div>}
          </div>
        </div>

        <div className="mt-6 text-sm text-gray-500">
          <p>Note: The backend handles background removal, cropping, DPI, and layout. This frontend is optimized for production builds (use `npm run build`).</p>
        </div>
      </div>
    </div>
  )
}
