from setuptools import setup
import setup_translate

pkg = 'Extensions.CacheFlush'
setup(name='enigma2-plugin-extensions-cacheflush',
       version='2.0.0',
       description='periodicaly flush box cache',
       package_dir={pkg: 'CacheFlush'},
       packages=[pkg],
       package_data={pkg: ['img/*.png', '*.png', '*.xml', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass=setup_translate.cmdclass,  # for translation
      )
