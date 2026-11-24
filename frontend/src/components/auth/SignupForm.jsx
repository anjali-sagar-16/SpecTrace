import { useState } from 'react';
import { Logo } from '../common/Logo';
import { InputField } from '../common/InputField';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function SignupForm({ onNavigateToLogin }) {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [apiNotice, setApiNotice] = useState(null);

  const validate = (dataToValidate = formData) => {
    const newErrors = {};

    if (!dataToValidate.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    } else if (dataToValidate.fullName.trim().length < 2) {
      newErrors.fullName = 'Full name must be at least 2 characters';
    }

    if (!dataToValidate.email.trim()) {
      newErrors.email = 'Work email is required';
    } else if (!EMAIL_REGEX.test(dataToValidate.email.trim())) {
      newErrors.email = 'Please enter a valid work email address';
    }

    if (!dataToValidate.password) {
      newErrors.password = 'Password is required';
    } else if (dataToValidate.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!dataToValidate.confirmPassword) {
      newErrors.confirmPassword = 'Confirming your password is required';
    } else if (dataToValidate.confirmPassword !== dataToValidate.password) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    return newErrors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updatedForm = { ...formData, [name]: value };
    setFormData(updatedForm);
    setApiNotice(null);

    // Live validation for touched fields
    if (touched[name] || (name === 'confirmPassword' && touched.password)) {
      const fieldErrors = validate(updatedForm);
      setErrors((prev) => ({
        ...prev,
        [name]: fieldErrors[name] || undefined,
        ...(name === 'password' && touched.confirmPassword
          ? { confirmPassword: fieldErrors.confirmPassword || undefined }
          : {}),
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
    setTouched({
      fullName: true,
      email: true,
      password: true,
      confirmPassword: true,
    });

    const validationErrors = validate(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    // UI prepared for future backend API integration
    setApiNotice({
      title: 'Registration Validation Passed',
      endpoint: 'POST /api/v1/auth/register',
      payload: {
        fullName: formData.fullName.trim(),
        email: formData.email.trim(),
        password: '••••••••••••',
      },
    });
  };

  return (
    <div className="auth-form-container">
      <div className="auth-card-header">
        <div className="auth-card-logo">
          <Logo size="small" />
        </div>
        <h1 className="auth-heading">Create your account.</h1>
        <p className="auth-subtitle">Get started with AI-driven change intelligence.</p>
      </div>

      {apiNotice && (
        <Alert
          type="success"
          title={apiNotice.title}
          onClose={() => setApiNotice(null)}
        >
          <p>
            Registration form passed frontend validation. Ready for backend integration at{' '}
            <code>{apiNotice.endpoint}</code>.
          </p>
          <div className="payload-preview">
            <span className="payload-label">Prepared Payload:</span>
            <pre className="payload-code">
              {JSON.stringify(apiNotice.payload, null, 2)}
            </pre>
          </div>
        </Alert>
      )}

      <form onSubmit={handleSubmit} noValidate className="auth-form">
        <InputField
          id="signup-fullName"
          name="fullName"
          type="text"
          label="Full name"
          placeholder="Linus Torvalds"
          value={formData.fullName}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.fullName ? errors.fullName : undefined}
          autoComplete="name"
          required
        />

        <InputField
          id="signup-email"
          name="email"
          type="email"
          label="Work email"
          placeholder="linus@kernel.org"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.email ? errors.email : undefined}
          autoComplete="email"
          required
        />

        <InputField
          id="signup-password"
          name="password"
          type="password"
          label="Password"
          placeholder="Minimum 8 characters"
          helperText="Must be at least 8 characters long"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.password ? errors.password : undefined}
          autoComplete="new-password"
          required
        />

        <InputField
          id="signup-confirmPassword"
          name="confirmPassword"
          type="password"
          label="Confirm password"
          placeholder="Re-enter your password"
          value={formData.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.confirmPassword ? errors.confirmPassword : undefined}
          autoComplete="new-password"
          required
        />

        <div className="auth-form-actions">
          <Button type="submit" variant="primary" fullWidth>
            Create Account
          </Button>
        </div>
      </form>

      <div className="auth-card-footer">
        <p className="switch-prompt">
          Already have an account?{' '}
          <button
            type="button"
            className="text-link switch-view-btn"
            onClick={onNavigateToLogin}
          >
            Sign in here
          </button>
        </p>
      </div>
    </div>
  );
}
