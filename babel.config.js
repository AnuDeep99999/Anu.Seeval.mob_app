module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      ['module-resolver', {
        extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
        alias: {
          '@': './src',        // already added earlier
          '~': './src',        // optional
          '@assets': './assets'
        }
      }],
      'react-native-reanimated/plugin' // keep last
    ],
  };
};
