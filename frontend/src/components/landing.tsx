'use client';
import React, { useState, ChangeEvent, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

type LandingProps = {
  
};

const Landing: React.FC = (LandingProps) => {
  const [fileOne, setFileOne] = useState<File | null>(null);
  const [fileTwo, setFileTwo] = useState<File | null>(null);
  const router = useRouter();


  const handleFileOneChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFileOne(selectedFile);
    }
  };

  const handleFileTwoChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFileTwo(selectedFile);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  
    if (fileOne && fileTwo) {
      const formData = new FormData();
      formData.append('fileOne', fileOne);
      formData.append('fileTwo', fileTwo);
  
      try {
        const response = await fetch('http://127.0.0.1:5000/upload', {
          method: 'POST',
          body: formData,
        });
        router.prefetch('/loading')
        if (response.ok) {
          console.log('Files uploaded successfully');
          // Navigate to the new page after successful upload
          router.push('/loading'); // Redirect to the desired route
        } else {
          console.error('Failed to upload files');
          router.push('/error');
          // Handle failure, e.g., display an error message to the user
        }
      } catch (error) {
        console.error('Error uploading files:', error);
        // Handle error, e.g., display an error message to the user
      }
    } else {
      alert('Please upload both files.');
    }
  };


  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-200">
      <h1 className="text-4xl font-bold mb-8 text-center">Steps to Analyze Your iMessage History</h1>
      <h2 className="text-lg text-gray-700 mb-6 text-center">
        We need two files. Due to macOS restrictions, we need you to upload the files.
      </h2>
      <form className="bg-white p-8 rounded shadow-md w-128" onSubmit={handleSubmit}>
        <div className="mb-6">
          <label htmlFor="fileOne" className="block text-gray-700 font-bold mb-2">
            Upload Contact Information from:
          </label>
          <p className="text-sm text-gray-500 mb-2">
            Users/<i>{'{'}your-username{'}'}</i>/Library/Application Support/AddressBook/AddressBook-v22.abcddb
          </p>
          <input
            type="file"
            id="fileOne"
            onChange={handleFileOneChange}
            className="border-gray-300 border rounded px-4 py-2 w-full"
          />
        </div>
        <div className="mb-6">
          <label htmlFor="fileTwo" className="block text-gray-700 font-bold mb-2">
            Upload Message History from:
          </label>
          <p className="text-sm text-gray-500 mb-2">
            Users/<i>{'{'}your-username{'}'}</i>/Library/Messages/chat.db
          </p>
          <input
            type="file"
            id="fileTwo"
            onChange={handleFileTwoChange}
            className="border-gray-300 border rounded px-4 py-2 w-full"
          />
        </div>
        <button
          type="submit"
          className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline w-full ${
            !(fileOne && fileTwo) ? 'opacity-50 cursor-not-allowed' : '' // Disable button if files are not selected
          }`}
          disabled={!(fileOne && fileTwo)}
        >
          Submit
        </button>
      </form>
    </div>
  );
};

export default Landing;
