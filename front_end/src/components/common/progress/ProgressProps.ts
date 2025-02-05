export interface ProgressProps {
  progress: number;
  message: string;
  description: string;
}

export interface CircularProgressProps {
  size: number;
  progress: number;
  trackWidth: number;
  trackColor: string;
  indicatorWidth: number;
  indicatorColor: string;
}
