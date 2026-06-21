import antfu from '@antfu/eslint-config';

export default antfu(
  {
    stylistic: {
      semi: true,
    },
    ignores: ['node_modules', '**/dist', '**/.venv'],
  },
  {
    files: ['**/*.{js,ts,jsx,tsx}'],
  },
);
