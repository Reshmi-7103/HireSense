"use client";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, useGLTF, useAnimations } from "@react-three/drei";
import { useEffect } from "react";
import { motion } from "framer-motion";

function AnimatedRobot() {
  const { scene, animations } = useGLTF("/robot.glb"); // ✅ Robot model
  const { actions } = useAnimations(animations, scene);

  useEffect(() => {
    // ✅ Always keep same size & position (fixes shrinking issue)
    scene.scale.set(2.3, 2.3, 2.3); // 🔹 bigger robot
    scene.position.set(0.8, -1.6, 0); // 🔹 moved right & slightly down

    // 🎬 Play first animation (if available)
    const firstAnimation = Object.keys(actions)[0];
    if (firstAnimation) {
      actions[firstAnimation].play();
    }
  }, [actions, scene]);

  return <primitive object={scene} />;
}

export default function Robot3D() {
  return (
    <motion.div
      initial={{ opacity: 0, x: 200, scale: 0.7, y: 50 }} // 🔹 starts from right & below
      animate={{ opacity: 1, x: 0, y: 0, scale: 1 }}       // 🔹 smooth slide-in animation
      transition={{
        type: "spring",
        stiffness: 90,
        damping: 18,
        duration: 1.3,
      }}
      className="absolute top-0.5 bottom-0 right-0 w-[850px] h-[850px]" // 🔹 larger canvas area
    >
      <Canvas camera={{ position: [0, 1, 6] }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[3, 3, 5]} intensity={1.2} />
        <AnimatedRobot />
        <Environment preset="city" />
        <OrbitControls enableZoom={false} enablePan={false} />
      </Canvas>
    </motion.div>
  );
}
