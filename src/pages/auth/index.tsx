import { useState, FormEvent } from 'react';
import { useRouter } from 'next/router';

export default function Auth() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'login' | 'signup' | 'otp'>('login');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const form = e.target as HTMLFormElement;
      const whatsapp = (form.elements.namedItem('whatsapp') as HTMLInputElement).value;
      const password = (form.elements.namedItem('password') as HTMLInputElement).value;

      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ whatsapp_number: whatsapp, password }),
      });

      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        router.push('/dashboard');
      } else {
        alert(data.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const form = e.target as HTMLFormElement;
      const formData = {
        full_name: (form.elements.namedItem('name') as HTMLInputElement).value,
        email: (form.elements.namedItem('email') as HTMLInputElement).value,
        whatsapp_number: (form.elements.namedItem('whatsapp') as HTMLInputElement).value,
        mobile_number: (form.elements.namedItem('mobile') as HTMLInputElement).value,
        password: (form.elements.namedItem('password') as HTMLInputElement).value,
      };

      const response = await fetch('/api/v1/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (response.ok) {
        setActiveTab('otp');
      } else {
        alert(data.detail || 'Signup failed');
      }
    } catch (error) {
      console.error('Signup error:', error);
      alert('An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Welcome to Payvry
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Secure P2P Payment Platform
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex border-b mb-4">
            <button
              onClick={() => setActiveTab('login')}
              className={`flex-1 py-2 text-center font-medium ${
                activeTab === 'login'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setActiveTab('signup')}
              className={`flex-1 py-2 text-center font-medium ${
                activeTab === 'signup'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Forms will go here - Login, Signup, and OTP forms */}
          {/* ... Rest of the form components */}
        </div>
      </div>
    </div>
  );
} 