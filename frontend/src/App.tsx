import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { RootLayout } from '@/layouts/RootLayout';
import { OverviewPage } from '@/pages/OverviewPage';
import { Login } from '@/pages/auth/Login';
import { PatientRegister } from '@/pages/auth/PatientRegister';
import { DoctorRegister } from '@/pages/auth/DoctorRegister';
import { RoleProtectedRoute } from '@/components/auth/RoleProtectedRoute';
import { PatientDashboard } from '@/pages/patient/PatientDashboard';
import { PatientAssignedDoctor } from '@/pages/patient/PatientAssignedDoctor';
import { DailyHealthCheck } from '@/pages/patient/DailyHealthCheck';
import { AdaptiveQuestionnaire } from '@/pages/patient/AdaptiveQuestionnaire';
import { EyeAnalysis } from '@/pages/patient/EyeAnalysis';
import { PatientEmergency } from '@/pages/patient/PatientEmergency';

// Doctor Portal Imports
import { DoctorDashboard } from '@/pages/doctor/DoctorDashboard';
import { DoctorPatientList } from '@/pages/doctor/DoctorPatientList';
import { DoctorPatientLayout } from '@/layouts/DoctorPatientLayout';
import { DoctorPatientOverview } from '@/pages/doctor/DoctorPatientOverview';
import { DoctorPatientHealth } from '@/pages/doctor/DoctorPatientHealth';
import { DoctorPatientQuestionnaire } from '@/pages/doctor/DoctorPatientQuestionnaire';
import { DoctorPatientEyeAnalysis } from '@/pages/doctor/DoctorPatientEyeAnalysis';
import { DoctorPatientRisk } from '@/pages/doctor/DoctorPatientRisk';
import { DoctorPatientNotes } from '@/pages/doctor/DoctorPatientNotes';
import { DoctorPatientReport } from '@/pages/doctor/DoctorPatientReport';
import { DoctorEmergencies } from '@/pages/doctor/DoctorEmergencies';

import { NotFoundPage } from '@/pages/error/NotFoundPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<RootLayout />}>
            <Route index element={<OverviewPage />} />
            <Route path="login" element={<Login />} />
            <Route path="register/patient" element={<PatientRegister />} />
            <Route path="register/doctor" element={<DoctorRegister />} />

            {/* Role-protected Patient Portal Routes */}
            <Route
              path="patient/dashboard"
              element={
                <RoleProtectedRoute allowedRole="PATIENT">
                  <PatientDashboard />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="patient/assigned-doctor"
              element={
                <RoleProtectedRoute allowedRole="PATIENT">
                  <PatientAssignedDoctor />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="patient/health-check"
              element={
                <RoleProtectedRoute allowedRole="PATIENT">
                  <DailyHealthCheck />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="patient/questionnaire"
              element={
                <RoleProtectedRoute allowedRole="PATIENT">
                  <AdaptiveQuestionnaire />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="patient/eye-analysis"
              element={
                <RoleProtectedRoute allowedRole="PATIENT">
                  <EyeAnalysis />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="patient/emergency"
              element={
                <RoleProtectedRoute allowedRole="PATIENT">
                  <PatientEmergency />
                </RoleProtectedRoute>
              }
            />

            {/* Role-protected Doctor Portal Routes */}
            <Route
              path="doctor/dashboard"
              element={
                <RoleProtectedRoute allowedRole="DOCTOR">
                  <DoctorDashboard />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="doctor/patients"
              element={
                <RoleProtectedRoute allowedRole="DOCTOR">
                  <DoctorPatientList />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="doctor/emergencies"
              element={
                <RoleProtectedRoute allowedRole="DOCTOR">
                  <DoctorEmergencies />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="doctor/patients/:id"
              element={
                <RoleProtectedRoute allowedRole="DOCTOR">
                  <DoctorPatientLayout />
                </RoleProtectedRoute>
              }
            >
              <Route index element={<DoctorPatientOverview />} />
              <Route path="health" element={<DoctorPatientHealth />} />
              <Route path="questionnaire" element={<DoctorPatientQuestionnaire />} />
              <Route path="eye-analysis" element={<DoctorPatientEyeAnalysis />} />
              <Route path="risk" element={<DoctorPatientRisk />} />
              <Route path="notes" element={<DoctorPatientNotes />} />
              <Route path="reports" element={<DoctorPatientReport />} />
            </Route>

            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
