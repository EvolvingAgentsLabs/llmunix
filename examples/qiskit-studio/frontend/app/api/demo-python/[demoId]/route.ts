/**
 * Copyright contributors to the Qiskit Studio project
 * SPDX-License-Identifier: Apache-2.0
 */

import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Define the mapping from demo IDs to Python files
const DEMO_PYTHON_FILES: Record<string, string> = {
  'chemistry-simulation': 'chemistry-SQD.py',
  'max-cut': 'MAX-CUT.py',
  'chsh-inequality': 'CHSH.py',
};

export async function GET(
  request: NextRequest,
  { params }: { params: { demoId: string } }
) {
  const { demoId } = params;
  
  const fileName = DEMO_PYTHON_FILES[demoId];
  if (!fileName) {
    return NextResponse.json(
      { error: 'Demo not found' }, 
      { status: 404 }
    );
  }

  try {
    const filePath = path.join(process.cwd(), 'lib', 'python', fileName);
    const pythonCode = fs.readFileSync(filePath, 'utf-8');
    
    return NextResponse.json({
      demoId,
      fileName,
      code: pythonCode
    });
  } catch (error) {
    console.error(`Failed to load Python file for demo ${demoId}:`, error);
    return NextResponse.json(
      { error: 'Failed to load demo code' }, 
      { status: 500 }
    );
  }
}