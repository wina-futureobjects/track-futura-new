import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { apiFetch } from '../../utils/api';
import { setAuthToken, setCurrentUser, UserRole } from '../../utils/auth';
import { 
  Eye, 
  EyeOff, 
  Shield, 
  TrendingUp, 
  BarChart3,
  Zap,
  ArrowRight
} from 'lucide-react';

// Define local types and auth implementation
interface LoginCredentials {
  username: string;
  password: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  global_role?: {
    role: UserRole;
    role_display: string;
  };
}

interface LoginResult {
  user: User;
}

// Local auth implementation
const useAuth = () => {
  const login = async (credentials: LoginCredentials): Promise<LoginResult> => {
    try {
      const response = await apiFetch('/api/users/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      
      // Save token using the auth utility
      setAuthToken(data.token);
      
      // Get user role and details
      const userProfileResp = await apiFetch('/api/users/profile/', {
        headers: {
          'Authorization': `Token ${data.token}`
        }
      });
      
      if (userProfileResp.ok) {
        const userProfileData = await userProfileResp.json();
        // Store complete user data including role
        const userData: User = {
          id: data.user_id,
          username: data.username,
          email: data.email,
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          global_role: userProfileData.user.global_role
        };
        
        // Save user data using auth utility
        setCurrentUser(userData);
        
        return { user: userData };
      } else {
        // If profile fetch fails, still store basic user info
        const userData: User = {
          id: data.user_id,
          username: data.username,
          email: data.email,
          first_name: data.first_name || '',
          last_name: data.last_name || ''
        };
        
        setCurrentUser(userData);
        return { user: userData };
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };
  
  return { login };
};

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
  });
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [rememberMe, setRememberMe] = useState<boolean>(false);
  const [isVisible, setIsVisible] = useState<boolean>(false);

  useEffect(() => {
    // Add custom CSS for animations
    const style = document.createElement('style');
    style.textContent = `
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(30px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      @keyframes fadeInLeft {
        from {
          opacity: 0;
          transform: translateX(-30px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }

      @keyframes fadeInRight {
        from {
          opacity: 0;
          transform: translateX(30px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }

      @keyframes fadeInCenter {
        from {
          opacity: 0;
          transform: translateY(20px) scale(0.95);
        }
        to {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
      }

      @keyframes floatingElement {
        0%, 100% {
          transform: translateY(0px) rotate(0deg);
        }
        50% {
          transform: translateY(-20px) rotate(10deg);
        }
      }

      @keyframes floatingElementDelayed {
        0%, 100% {
          transform: translateY(0px) rotate(0deg);
        }
        50% {
          transform: translateY(-30px) rotate(-10deg);
        }
      }

      @keyframes pulseGlow {
        0%, 100% {
          opacity: 0.3;
          transform: scale(1);
        }
        50% {
          opacity: 0.1;
          transform: scale(1.1);
        }
      }

      .floating-1 {
        animation: floatingElement 6s ease-in-out infinite;
      }

      .floating-2 {
        animation: floatingElementDelayed 8s ease-in-out infinite;
      }

      .glow-pulse {
        animation: pulseGlow 4s ease-in-out infinite;
      }

      .slide-in-left {
        animation: fadeInLeft 0.8s ease-out forwards;
      }

      .slide-in-right {
        animation: fadeInRight 0.8s ease-out forwards;
      }

      .fade-in-center {
        animation: fadeInCenter 1s ease-out forwards;
      }

      .shake-error {
        animation: shake 0.5s ease-in-out;
      }

      @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
      }
    `;
    document.head.appendChild(style);

    setIsVisible(true);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(credentials);
      // Check if user has admin role and redirect accordingly
      const userRole = result.user.global_role?.role;
      
      if (userRole === 'super_admin') {
        navigate('/admin/super');
      } else if (userRole === 'tenant_admin') {
        // Fetch the tenant admin's organizations and redirect to the first one's projects page
        try {
          const response = await apiFetch('/api/users/organizations/');
          if (response.ok) {
            const data = await response.json();
            const organizations = Array.isArray(data) ? data : (data.results || []);
            
            if (organizations.length > 0) {
              // Redirect to the first organization's projects page
              navigate(`/organizations/${organizations[0].id}/projects`);
            } else {
              // If no organizations, redirect to main page
              navigate('/');
            }
          } else {
            // If API call fails, redirect to main page
            navigate('/');
          }
        } catch (error) {
          console.error('Error fetching organizations:', error);
          navigate('/');
        }
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Enhanced Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-gray-900 to-slate-900" />
      <div className="absolute inset-0 bg-gradient-to-tr from-emerald-900/20 via-transparent to-violet-900/20" />
      <div className="absolute inset-0 bg-gradient-to-bl from-cyan-900/10 via-transparent to-transparent" />
      
      {/* Animated floating elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-emerald-500/30 to-cyan-500/30 rounded-full mix-blend-multiply filter blur-3xl floating-1" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-tr from-violet-500/30 to-purple-500/30 rounded-full mix-blend-multiply filter blur-3xl floating-2" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 rounded-full mix-blend-multiply filter blur-3xl glow-pulse" />
      </div>

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: `radial-gradient(circle at 1px 1px, white 1px, transparent 0)`,
        backgroundSize: '24px 24px'
      }} />

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-20 items-center">
            
            {/* Left side - Branding and features */}
            <div className={`hidden lg:block space-y-12 ${isVisible ? 'slide-in-left' : 'opacity-0'}`}>
              {/* Logo and title */}
              <div className="space-y-8">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-cyan-600 rounded-3xl blur-lg opacity-50 glow-pulse" />
                    <div className="relative p-4 bg-gradient-to-br from-emerald-500 to-cyan-600 rounded-3xl shadow-2xl">
                      <TrendingUp className="w-10 h-10 text-white" />
                    </div>
                  </div>
                  <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent">
                      Track Futura
                    </h1>
                    <p className="text-xl text-gray-300 font-medium">Analytics Platform</p>
                  </div>
                </div>

                {/* Main headline */}
                <div className="space-y-6">
                  <h2 className="text-5xl lg:text-6xl font-bold text-white leading-tight">
                    Transform Your
                    <span className="block bg-gradient-to-r from-emerald-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent">
                      Data Analytics
                    </span>
                  </h2>
                  <p className="text-xl text-gray-300 leading-relaxed max-w-lg">
                    Comprehensive data collection and insights across all major social platforms. 
                    Monitor, analyze, and optimize your social media performance with cutting-edge AI.
                  </p>
                </div>
              </div>

              {/* Features */}
              <div className="space-y-6">
                {[
                  {
                    icon: <BarChart3 className="w-6 h-6" />,
                    title: "Multi-Platform Analytics",
                    description: "Unified dashboard for Facebook, Instagram, LinkedIn, TikTok, and more.",
                    gradient: "from-emerald-500 to-green-600"
                  },
                  {
                    icon: <Shield className="w-6 h-6" />,
                    title: "Enterprise Security",
                    description: "Bank-level encryption and SOC 2 compliance for your data protection.",
                    gradient: "from-cyan-500 to-blue-600"
                  },
                  {
                    icon: <Zap className="w-6 h-6" />,
                    title: "Real-time Insights",
                    description: "AI-powered notifications and live data streams as events happen.",
                    gradient: "from-violet-500 to-purple-600"
                  }
                ].map((feature, index) => (
                  <div 
                    key={index}
                    className="flex items-start gap-4 group hover:translate-x-2 transition-transform duration-300 opacity-0"
                    style={{ animation: `fadeInLeft 0.8s ease-out ${0.4 + index * 0.15}s forwards` }}
                  >
                    <div className={`p-3 rounded-2xl bg-gradient-to-br ${feature.gradient} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      {feature.icon}
                    </div>
                    <div className="space-y-1">
                      <h3 className="text-xl font-semibold text-white group-hover:text-emerald-300 transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-gray-300 leading-relaxed">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Footer */}
              <div className="pt-8 border-t border-gray-700/50">
                <p className="text-gray-400">
                  © 2025 Future Objects. Built for the future of analytics.
                </p>
              </div>
            </div>

            {/* Right side - Login form (Centered) */}
            <div className="w-full flex items-center justify-center">
              <div className={`w-full max-w-md mx-auto ${isVisible ? 'fade-in-center' : 'opacity-0'}`}>
                
                {/* Mobile header */}
                <div className="lg:hidden text-center mb-12 opacity-0" style={{ animation: 'fadeInUp 0.8s ease-out 0.2s forwards' }}>
                  <div className="flex items-center justify-center gap-3 mb-6">
                    <div className="relative">
                      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-cyan-600 rounded-2xl blur-md opacity-50" />
                      <div className="relative p-3 bg-gradient-to-br from-emerald-500 to-cyan-600 rounded-2xl">
                        <TrendingUp className="w-8 h-8 text-white" />
                      </div>
                    </div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                      Track Futura
                    </h1>
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-3">Welcome Back</h2>
                  <p className="text-gray-300 text-lg">Sign in to continue to your dashboard</p>
                </div>

                {/* Login form card */}
                <div className="relative group">
                  {/* Glow effect */}
                  <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 via-cyan-500 to-violet-500 rounded-3xl blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-500" />
                  
                  <div className="relative backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl overflow-hidden">
                    {/* Header */}
                    <div className="p-10 text-center border-b border-white/10">
                      <h2 className="text-3xl font-bold text-white mb-3">Welcome Back</h2>
                      <p className="text-gray-300 text-lg">Sign in to continue to your dashboard</p>
                    </div>

                    {/* Error message */}
                    {error && (
                      <div className="mx-10 mt-8 p-4 bg-red-500/20 border border-red-500/30 rounded-2xl shake-error">
                        <p className="text-red-200 text-sm font-medium">{error}</p>
                      </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="p-10 space-y-8">
                      <div className="space-y-6">
                        <div className="group">
                          <Label htmlFor="username" className="text-white font-semibold text-lg mb-3 block">
                            Username
                          </Label>
                          <div className="relative">
                            <Input
                              id="username"
                              name="username"
                              type="text"
                              required
                              value={credentials.username}
                              onChange={handleChange}
                              placeholder="Enter your username"
                              className="w-full h-14 bg-white/10 border-white/20 text-white text-lg placeholder:text-gray-300 focus:border-emerald-400 focus:ring-emerald-400/20 rounded-2xl transition-all duration-300 group-hover:bg-white/15"
                            />
                          </div>
                        </div>

                        <div className="group">
                          <div className="flex items-center justify-between mb-3">
                            <Label htmlFor="password" className="text-white font-semibold text-lg">
                              Password
                            </Label>
                            <Link to="#" className="text-emerald-300 hover:text-emerald-200 transition-colors font-medium">
                              Forgot password?
                            </Link>
                          </div>
                          <div className="relative">
                            <Input
                              id="password"
                              name="password"
                              type={showPassword ? 'text' : 'password'}
                              required
                              value={credentials.password}
                              onChange={handleChange}
                              placeholder="Enter your password"
                              className="w-full h-14 bg-white/10 border-white/20 text-white text-lg placeholder:text-gray-300 focus:border-emerald-400 focus:ring-emerald-400/20 rounded-2xl pr-14 transition-all duration-300 group-hover:bg-white/15"
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-300 hover:text-white transition-colors p-1"
                            >
                              {showPassword ? <EyeOff className="w-6 h-6" /> : <Eye className="w-6 h-6" />}
                            </button>
                          </div>
                        </div>

                        <div className="flex items-center justify-between pt-2">
                          <div className="flex items-center">
                            <input
                              id="remember_me"
                              name="remember_me"
                              type="checkbox"
                              checked={rememberMe}
                              onChange={(e) => setRememberMe(e.target.checked)}
                              className="h-5 w-5 rounded-lg border-white/20 bg-white/10 text-emerald-600 focus:ring-emerald-500 focus:ring-offset-0"
                            />
                            <label htmlFor="remember_me" className="ml-3 text-gray-300 font-medium">
                              Remember me
                            </label>
                          </div>
                        </div>

                        <Button
                          type="submit"
                          disabled={isLoading}
                          className="group relative w-full h-14 bg-gradient-to-r from-emerald-600 via-cyan-600 to-violet-600 hover:from-emerald-500 hover:via-cyan-500 hover:to-violet-500 text-white font-semibold text-lg rounded-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-2xl hover:shadow-emerald-500/25 hover:scale-[1.02] overflow-hidden"
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                          {isLoading ? (
                            <div className="flex items-center gap-3">
                              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                              Signing in...
                            </div>
                          ) : (
                            <div className="flex items-center gap-3">
                              Sign In
                              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                            </div>
                          )}
                        </Button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login; 