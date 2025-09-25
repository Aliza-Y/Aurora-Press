import { NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import connectDB from '@/lib/mongodb';
import User from '@/models/User';

export async function POST(req: Request) {
  try {
    const { firstName, lastName, email, password, confirmPassword } = await req.json();

    // Validate all required fields
    const missingFields = [];
    if (!firstName?.trim()) missingFields.push('First Name');
    if (!lastName?.trim()) missingFields.push('Last Name');
    if (!email?.trim()) missingFields.push('Email');
    if (!password) missingFields.push('Password');
    if (!confirmPassword) missingFields.push('Confirm Password');

    if (missingFields.length > 0) {
      return NextResponse.json(
        { 
          error: 'Missing required fields',
          message: `Please fill in all required fields: ${missingFields.join(', ')}`,
          missingFields
        },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      );
    }

    // Validate password match
    if (password !== confirmPassword) {
      return NextResponse.json(
        { error: 'Passwords do not match' },
        { status: 400 }
      );
    }

    // Validate password requirements
    if (password.length < 8) {
      return NextResponse.json(
        { 
          error: 'Password too short',
          message: 'Password must be at least 8 characters long'
        },
        { status: 400 }
      );
    }

    // Comprehensive password validation
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(password)) {
      return NextResponse.json(
        { 
          error: 'Invalid password format',
          message: 'Password must contain:',
          requirements: {
            minLength: '8 characters minimum',
            uppercase: 'At least one uppercase letter (A-Z)',
            lowercase: 'At least one lowercase letter (a-z)',
            number: 'At least one number (0-9)',
            specialChar: 'At least one special character (@$!%*?&)'
          }
        },
        { status: 400 }
      );
    }

    await connectDB();

    // Check if user already exists
    const existingUser = await User.findOne({ email: email.toLowerCase() });
    if (existingUser) {
      return NextResponse.json(
        { 
          error: 'User already exists',
          message: 'An account with this email already exists'
        },
        { status: 400 }
      );
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user with all fields
    const user = await User.create({
      name: `${firstName} ${lastName}`,
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      email: email.toLowerCase().trim(),
      password: hashedPassword,
      isFirstLogin: true,
      lastLogin: null,
      profileCompleted: false,
      createdAt: new Date()
    });

    return NextResponse.json(
      { 
        message: 'User created successfully',
        user: {
          id: user._id,
          firstName: user.firstName,
          lastName: user.lastName,
          email: user.email,
          isFirstLogin: user.isFirstLogin,
          profileCompleted: user.profileCompleted
        }
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('Registration error:', error);
    return NextResponse.json(
      { 
        error: 'Error creating user',
        message: 'An unexpected error occurred during registration'
      },
      { status: 500 }
    );
  }
} 