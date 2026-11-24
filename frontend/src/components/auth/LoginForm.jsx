import { useState } from 'react';
import { Logo } from '../common/Logo';
import { InputField } from '../common/InputField';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function LoginForm({ onNavigateToSignup, onNavigateToDashboard }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [apiNotice, setApiNotice] = useState(null);
  const [forgotPasswordNotice, setForgotPasswordNotice] = useState(false);

  const validate = (dataToValidate = formData) => {
    const newErrors = {};

    if (!dataToValidate.email.trim()) {
      newErrors.email = 'Email address is required';
    } else if (!EMAIL_REGEX.test(dataToValidate.email.trim())) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!dataToValidate.password) {
      newErrors.password = 'Password is required';
    } else if (dataToValidate.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    return newErrors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setApiNotice(null);

    // Live validation if field was touched
    if (touched[name]) {
      const fieldErrors = validate({ ...formData, [name]: value });
      setErrors((prev) => ({
        ...prev,
        [name]: fieldErrors[name] || undefined,
      }));
    }
  };

  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    const fieldErrors = validate(formData);
    setErrors((prev) => ({
      ...prev,
      [name]: fieldErrors[name] || undefined,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setTouched({ email: true, password: true });

    const validationErrors = validate(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    // UI prepared for future backend API integration
    setApiNotice({
      title: 'Frontend Validation Passed',
      endpoint: 'POST /api/v1/auth/login',
      payload: {
        email: formData.email.trim(),
        password: '••••••••••••',
      },
    });
  };

  const handleForgotPasswordClick = (e) => {
    e.preventDefault();
    setForgotPasswordNotice(true);
  };

  return (
    <div className="auth-form-container">
      <div className="auth-card-header">
        <div className="auth-card-logo">
          <Logo size="small" />
        </div>
        <h1 className="auth-heading">Welcome back.</h1>
        <p className="auth-subtitle">Sign in to your SpecTrace workspace.</p>
      </div>

      {apiNotice && (
        <Alert
          type="success"
          title={apiNotice.title}
          onClose={() => setApiNotice(null)}
        >
          <p>
            Form input is valid. The UI is ready for backend integration at{' '}
            <code>{apiNotice.endpoint}</code>.
          </p>
          <div className="payload-preview">
            <span className="payload-label">Prepared Payload:</span>
            <pre className="payload-code">
              {JSON.stringify(apiNotice.payload, null, 2)}
            </pre>
          </div>
          {onNavigateToDashboard && (
            <div style={{ marginTop: '12px' }}>
              <Button variant="primary" fullWidth onClick={onNavigateToDashboard}>
                Open SpecTrace Dashboard &rarr;
              </Button>
            </div>
          )}
        </Alert>
      )}

      {forgotPasswordNotice && (
        <Alert
          type="info"
          title="Password Recovery"
          onClose={() => setForgotPasswordNotice(false)}
        >
          Password recovery endpoint will be connected when the backend authentication service is implemented.
        </Alert>
      )}

      <form onSubmit={handleSubmit} noValidate className="auth-form">
        <InputField
          id="login-email"
          name="email"
          type="email"
          label="Email address"
          placeholder="name@company.com"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.email ? errors.email : undefined}
          autoComplete="email"
          required
        />

        <InputField
          id="login-password"
          name="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.password ? errors.password : undefined}
          autoComplete="current-password"
          required
          rightElement={
            <button
              type="button"
              className="text-link forgot-password-link"
              onClick={handleForgotPasswordClick}
            >
              Forgot password?
            </button>
          }
        />

        <div className="auth-form-actions">
          <Button type="submit" variant="primary" fullWidth>
            Sign In
          </Button>
        </div>
      </form>

      <div className="auth-card-footer">
        <p className="switch-prompt">
          Don&apos;t have an account?{' '}
          <button
            type="button"
            className="text-link switch-view-btn"
            onClick={onNavigateToSignup}
          >
            Sign up for SpecTrace
          </button>
        </p>

        {onNavigateToDashboard && (
          <div style={{ marginTop: '12px' }}>
            <button
              type="button"
              className="text-link"
              style={{ fontSize: '12.5px', color: '#64748b' }}
              onClick={onNavigateToDashboard}
            >
              Explore Dashboard Preview &rarr;
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
