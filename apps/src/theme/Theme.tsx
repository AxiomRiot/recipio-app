import type { ReactNode } from 'react';
import { ThemeProvider } from 'styled-components';
import { colors } from './foundation/colors';
import { typography } from './foundation/typography';

interface ThemeProps {
  children: ReactNode;
}

const theme = {
  colors,
  typography,
};

export function Theme({ children }: ThemeProps) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
