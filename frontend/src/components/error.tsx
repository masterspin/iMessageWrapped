import { NextPage } from 'next';
import Link from 'next/link';

type ErrorProps = {
  
};

const Error: React.FC = (ErrorProps) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-200">
      <div className="max-w-md w-full text-center p-8 bg-white rounded shadow-md">
        <h1 className="text-4xl font-bold mb-6">
            An error has occurred
        </h1>
        <p className="text-lg mb-4">
          Sorry, something went wrong. Please try again or go back to the{' '}
          <Link href="/">
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded-full">Home Page</button>
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Error;
